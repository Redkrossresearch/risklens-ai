import pytest

from risklens_db import (
    TechnicalFindingInput,
    build_query_text,
    normalize_query_text,
    verify_access,
)


def test_verify_access_accepts_correct_token() -> None:
    assert verify_access(
        "RiskLensSecureToken2026-Local-Test-Key",
        "RiskLensSecureToken2026-Local-Test-Key",
    )


def test_verify_access_rejects_wrong_token() -> None:
    assert not verify_access(
        "wrong-token",
        "RiskLensSecureToken2026-Local-Test-Key",
    )


def test_verify_access_rejects_empty_token() -> None:
    assert not verify_access(
        "",
        "RiskLensSecureToken2026-Local-Test-Key",
    )


def test_normalize_query_text_removes_extra_spaces() -> None:
    assert normalize_query_text("  weak     password\n\npolicy  ") == "weak password policy"


def test_normalize_query_text_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        normalize_query_text("   ")


def test_normalize_query_text_rejects_too_long_text() -> None:
    with pytest.raises(ValueError):
        normalize_query_text("a" * 1501)


def test_technical_finding_input_accepts_valid_data() -> None:
    finding = TechnicalFindingInput(
        vulnerability_title="Weak Password Policy",
        description="Passwords are shorter than eight characters.",
        severity="Medium",
    )

    assert finding.vulnerability_title == "Weak Password Policy"
    assert finding.severity == "Medium"


def test_technical_finding_input_rejects_invalid_severity() -> None:
    with pytest.raises(ValueError):
        TechnicalFindingInput(
            vulnerability_title="Weak Password Policy",
            description="Passwords are shorter than eight characters.",
            severity="Very Bad",
        )


def test_build_query_text_contains_finding_details() -> None:
    finding = TechnicalFindingInput(
        vulnerability_title="Weak Password Policy",
        description="Passwords are shorter than eight characters.",
        severity="High",
        cve="CVE-2026-1234",
    )

    query = build_query_text(finding)

    assert "Weak Password Policy" in query
    assert "High" in query
    assert "Passwords are shorter" in query
    assert "CVE-2026-1234" in query