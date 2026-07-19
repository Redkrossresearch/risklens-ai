"""RiskLens compliance report generation."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field

from rag_pipeline import RAGResponse


class ComplianceMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework: str
    control_id: str
    source_file: str | None = None
    page: int | None = None
    confidence_label: str
    confidence_score: int = Field(..., ge=0, le=100)
    evidence: str


class ComplianceReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    generated_at: str
    report_type: str
    finding_title: str
    severity: str
    mapped_results_count: int
    executive_summary: str
    mappings: list[ComplianceMapping]
    production_notes: list[str]


def generate_compliance_report(response: RAGResponse) -> ComplianceReport:
    """Generate structured compliance report from RAG response."""

    mappings = [
        ComplianceMapping(
            framework=item.framework,
            control_id=item.control_id,
            source_file=item.source_file,
            page=item.page,
            confidence_label=item.confidence_label,
            confidence_score=item.confidence_score,
            evidence=item.evidence,
        )
        for item in response.context.items
    ]

    return ComplianceReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        report_type="RiskLens Compliance Mapping Report",
        finding_title=response.finding_title,
        severity=response.severity,
        mapped_results_count=response.mapped_results_count,
        executive_summary=response.summary,
        mappings=mappings,
        production_notes=[
            "TLS should be enforced by reverse proxy or API gateway.",
            "Production rate limiting should use Redis, NGINX, Cloudflare, or API gateway.",
            "OAuth should be integrated through an identity provider such as Azure AD, Auth0, or Google.",
            "WAF and DDoS protection should be configured at the network/cloud edge.",
            "CORS should allow only approved frontend origins.",
            "Request body limits should be enforced at both API and reverse proxy layers.",
            "Audit logs should avoid storing secrets or full sensitive findings.",
        ],
    )


def report_to_markdown(report: ComplianceReport) -> str:
    """Convert report to Markdown."""

    lines = [
        "# RiskLens Compliance Mapping Report",
        "",
        f"Generated At: {report.generated_at}",
        f"Finding: {report.finding_title}",
        f"Severity: {report.severity}",
        f"Mapped Results: {report.mapped_results_count}",
        "",
        "## Executive Summary",
        "",
        report.executive_summary,
        "",
        "## Compliance Mappings",
    ]

    for index, mapping in enumerate(report.mappings, start=1):
        lines.extend(
            [
                "",
                f"### Mapping {index}",
                "",
                f"- Framework: {mapping.framework}",
                f"- Control ID: {mapping.control_id}",
                f"- Source File: {mapping.source_file}",
                f"- Page: {mapping.page}",
                f"- Confidence: {mapping.confidence_label} ({mapping.confidence_score}/100)",
                "",
                "Evidence:",
                "",
                mapping.evidence,
            ]
        )

    lines.extend(["", "## Production Readiness Notes", ""])

    for note in report.production_notes:
        lines.append(f"- {note}")

    return "\n".join(lines)