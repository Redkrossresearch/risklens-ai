import re

VALID_SEVERITIES = {
    "Critical",
    "High",
    "Medium",
    "Low",
    "Informational"
}


def validate_severity(severity):
    """
    Returns True if severity is valid.
    """
    return str(severity).strip() in VALID_SEVERITIES


def validate_cve(cve):
    """
    Validates CVE format.
    Example:
    CVE-2024-1234
    CVE-2025-12345
    """

    pattern = r"^CVE-\d{4}-\d{4,}$"

    return bool(re.match(pattern, str(cve).strip()))