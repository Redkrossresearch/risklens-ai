"""Secure RiskLens RAG pipeline for compliance mapping."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from risklens_db import (
    ComplianceMatchSchema,
    SecureComplianceDatabase,
    TechnicalFindingInput,
)


logger = logging.getLogger("risklens_rag")


@dataclass(frozen=True)
class RAGConfig:
    max_results: int = 5
    max_evidence_chars: int = 700
    max_summary_chars: int = 1800
    max_total_context_chars: int = 2500
    min_token_length: int = 32
    high_confidence_distance: float = 1.10
    medium_confidence_distance: float = 1.35
    max_distance_for_score: float = 2.0


ALLOWED_FRAMEWORKS = {"NIST", "CIS", "ISO27001", "OTHER"}


class ComplianceContextItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework: str
    control_id: str
    source_file: str | None = None
    page: int | None = None
    distance: float | None = None
    confidence_label: Literal["High", "Medium", "Low"]
    confidence_score: int = Field(..., ge=0, le=100)
    evidence: str


class ComplianceContext(BaseModel):
    model_config = ConfigDict(extra="forbid")

    finding_title: str
    severity: str
    llm_context_string: str
    items: list[ComplianceContextItem]


class RAGResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["Success"]
    finding_title: str
    severity: str
    mapped_results_count: int
    summary: str
    context: ComplianceContext


class RAGErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["Error"]
    error_type: str
    message: str


def load_token_from_environment(config: RAGConfig) -> str:
    token = os.getenv("RISKLENS_SHARED_SECRET", "").strip()

    if not isinstance(token, str) or not token:
        raise RuntimeError("RISKLENS_SHARED_SECRET is not set.")

    if len(token) < config.min_token_length:
        raise RuntimeError(
            f"RISKLENS_SHARED_SECRET must be at least {config.min_token_length} characters."
        )

    return token


def clean_output_text(text: str, max_length: int) -> str:
    if not isinstance(text, str):
        return ""

    cleaned = text.replace("\x00", "")
    cleaned = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if len(cleaned) > max_length:
        return cleaned[:max_length].rstrip() + "..."

    return cleaned


def normalize_framework(framework: str) -> str:
    return framework if framework in ALLOWED_FRAMEWORKS else "OTHER"


def confidence_score(distance: float | None, config: RAGConfig) -> int:
    if distance is None:
        return 0

    bounded_distance = max(0.0, min(distance, config.max_distance_for_score))
    score = (1.0 - (bounded_distance / config.max_distance_for_score)) * 100

    return int(round(max(0.0, min(score, 100.0))))


def confidence_label(
    distance: float | None,
    config: RAGConfig,
) -> Literal["High", "Medium", "Low"]:
    if distance is None:
        return "Low"

    if distance <= config.high_confidence_distance:
        return "High"

    if distance <= config.medium_confidence_distance:
        return "Medium"

    return "Low"


def get_optional_attr(obj: object, name: str, default: object = None) -> object:
    return getattr(obj, name, default)


def safe_exception_name(error: Exception) -> str:
    return error.__class__.__name__


class RiskLensRAGPipeline:
    """Secure RAG pipeline for RiskLens compliance mapping."""

    def __init__(
        self,
        db: SecureComplianceDatabase,
        *,
        user_token: str | None = None,
        config: RAGConfig = RAGConfig(),
    ) -> None:
        self.db = db
        self.config = config
        self.user_token = user_token or load_token_from_environment(config)

    def build_compliance_context(
        self,
        finding: TechnicalFindingInput,
        *,
        n_results: int = 3,
        framework_filter: Literal["NIST", "CIS", "ISO27001", "OTHER"] | None = None,
    ) -> ComplianceContext:
        if not 1 <= n_results <= self.config.max_results:
            raise ValueError(f"n_results must be between 1 and {self.config.max_results}")

        if framework_filter is not None and framework_filter not in ALLOWED_FRAMEWORKS:
            raise ValueError(f"Unsupported framework_filter: {framework_filter}")

        matches = self.db.secure_query_v2(
            user_token=self.user_token,
            finding=finding,
            n_results=n_results,
        )

        if framework_filter is not None:
            matches = [match for match in matches if match.framework == framework_filter]

        sorted_matches = sorted(matches, key=self._match_sort_key)

        items: list[ComplianceContextItem] = []
        llm_parts: list[str] = []
        total_context_chars = 0

        for match in sorted_matches:
            if total_context_chars >= self.config.max_total_context_chars:
                break

            evidence = clean_output_text(
                match.matched_rule,
                self.config.max_evidence_chars,
            )

            remaining_chars = self.config.max_total_context_chars - total_context_chars

            if len(evidence) > remaining_chars:
                evidence = clean_output_text(evidence, remaining_chars)

            total_context_chars += len(evidence)

            source_file_value = get_optional_attr(match, "source_file", None)
            page_value = get_optional_attr(match, "page", None)
            page = page_value if isinstance(page_value, int) else None

            item = ComplianceContextItem(
                framework=normalize_framework(match.framework),
                control_id=match.control_id or "N/A",
                source_file=str(source_file_value) if source_file_value is not None else None,
                page=page,
                distance=match.distance,
                confidence_label=confidence_label(match.distance, self.config),
                confidence_score=confidence_score(match.distance, self.config),
                evidence=evidence,
            )

            items.append(item)

            llm_parts.append(
                "\n".join(
                    [
                        f"Framework: {item.framework}",
                        f"Control: {item.control_id}",
                        f"Source: {item.source_file}",
                        f"Page: {item.page}",
                        f"Confidence: {item.confidence_label} ({item.confidence_score}/100)",
                        f"Evidence: {item.evidence}",
                    ]
                )
            )

        llm_context_string = "\n\n---\n\n".join(llm_parts)
        llm_context_string = clean_output_text(
            llm_context_string,
            self.config.max_total_context_chars,
        )

        return ComplianceContext(
            finding_title=finding.vulnerability_title,
            severity=finding.severity,
            llm_context_string=llm_context_string,
            items=items,
        )

    def map_compliance(
        self,
        finding: TechnicalFindingInput,
        *,
        n_results: int = 3,
        framework_filter: Literal["NIST", "CIS", "ISO27001", "OTHER"] | None = None,
    ) -> RAGResponse:
        context = self.build_compliance_context(
            finding=finding,
            n_results=n_results,
            framework_filter=framework_filter,
        )

        summary = self._build_summary(finding, context)

        logger.info("RiskLens RAG mapping completed.")

        return RAGResponse(
            status="Success",
            finding_title=finding.vulnerability_title,
            severity=finding.severity,
            mapped_results_count=len(context.items),
            summary=summary,
            context=context,
        )

    def map_compliance_safe(
        self,
        finding: TechnicalFindingInput,
        *,
        n_results: int = 3,
        framework_filter: Literal["NIST", "CIS", "ISO27001", "OTHER"] | None = None,
    ) -> RAGResponse | RAGErrorResponse:
        try:
            return self.map_compliance(
                finding=finding,
                n_results=n_results,
                framework_filter=framework_filter,
            )

        except PermissionError:
            logger.warning("Unauthorized RAG request blocked.")
            return RAGErrorResponse(
                status="Error",
                error_type="AUTHENTICATION_ERROR",
                message="Access denied.",
            )

        except ValueError as error:
            logger.warning("Invalid RAG request: %s", safe_exception_name(error))
            return RAGErrorResponse(
                status="Error",
                error_type="VALIDATION_ERROR",
                message=str(error),
            )

        except Exception as error:
            logger.error("Unexpected RAG pipeline failure: %s", safe_exception_name(error))
            return RAGErrorResponse(
                status="Error",
                error_type="INTERNAL_ERROR",
                message="RAG compliance mapping failed.",
            )

    def _match_sort_key(self, match: ComplianceMatchSchema) -> tuple[int, float, str, str]:
        distance = match.distance if match.distance is not None else 999.0

        return (
            -confidence_score(match.distance, self.config),
            distance,
            match.framework,
            match.control_id,
        )

    def _build_summary(
        self,
        finding: TechnicalFindingInput,
        context: ComplianceContext,
    ) -> str:
        if not context.items:
            return (
                "No strong compliance mapping was found for this finding. "
                "Manual compliance review is recommended."
            )

        top = context.items[0]

        summary = f"""
Compliance Mapping Summary

Finding:
{clean_output_text(finding.vulnerability_title, 200)}

Severity:
{finding.severity}

Primary Mapping:
The finding maps most closely to {top.framework} control {top.control_id}.

Confidence:
{top.confidence_label} ({top.confidence_score}/100)

Why this mapping was selected:
The finding describes: "{clean_output_text(finding.description, 350)}"

The retrieved compliance evidence is related to the same security theme. The evidence is used only as reference material, not as executable instruction.

Recommended Compliance Action:
1. Review the mapped control.
2. Compare the system behavior against the control requirement.
3. Record evidence of compliance or non-compliance.
4. If a gap exists, create a remediation task with owner and due date.

Primary Evidence Source:
Framework: {top.framework}
Control: {top.control_id}
Source File: {top.source_file}
Page: {top.page}

Security Note:
Retrieved document text is isolated as evidence and does not control application behavior.
""".strip()

        return clean_output_text(summary, self.config.max_summary_chars)


def main() -> None:
    db = SecureComplianceDatabase()
    pipeline = RiskLensRAGPipeline(db=db)

    finding = TechnicalFindingInput(
        vulnerability_title="Weak Password Policy",
        description=(
            "The application allows short passwords and does not enforce "
            "strong access control requirements."
        ),
        severity="High",
        cve=None,
    )

    response = pipeline.map_compliance_safe(
        finding=finding,
        n_results=3,
        framework_filter=None,
    )

    print("\n--- RiskLens Secure RAG Compliance Mapping ---")

    if isinstance(response, RAGErrorResponse):
        print(f"Status     : {response.status}")
        print(f"Error Type : {response.error_type}")
        print(f"Message    : {response.message}")
        return

    print(response.summary)

    print("\n--- LLM Context String ---")
    print(response.context.llm_context_string)

    print("\n--- Structured Context Items ---")

    for index, item in enumerate(response.context.items, start=1):
        print(f"\nMatch {index}")
        print(f"Framework  : {item.framework}")
        print(f"Control    : {item.control_id}")
        print(f"Source     : {item.source_file}")
        print(f"Page       : {item.page}")
        print(f"Distance   : {item.distance}")
        print(f"Confidence : {item.confidence_label} ({item.confidence_score}/100)")
        print(f"Evidence   : {item.evidence}")


if __name__ == "__main__":
    main()