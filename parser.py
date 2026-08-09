import pandas as pd
import uuid

from models import VulnerabilityModel


def clean_value(value, default="N/A"):
    """
    Convert empty/NaN values into a safe default.
    """
    if pd.isna(value) or str(value).strip() == "":
        return default

    return str(value).strip()


def parse_csv(file_path: str):
    df = pd.read_csv(file_path, encoding="utf-16")

    vulnerabilities = []

    for index, (_, row) in enumerate(df.iterrows(), start=1):

        vuln = VulnerabilityModel(
            vulnerability_id=f"VULN-{index:03d}",

            title=clean_value(
                row.get(
                    "title",
                    row.get(
                        "Name",
                        row.get("Plugin Name", "Unknown")
                    )
                ),
                "Unknown"
            ),

            cve=clean_value(
                row.get(
                    "cve",
                    row.get("CVE", "N/A")
                ),
                "N/A"
            ),

            severity=clean_value(
                row.get(
                    "severity",
                    row.get("Severity", "Unknown")
                ),
                "Unknown"
            ),

            host=clean_value(
                row.get(
                    "host",
                    row.get(
                        "Host",
                        row.get("IP Address", "Unknown")
                    )
                ),
                "Unknown"
            ),

            description=clean_value(
                row.get(
                    "description",
                    row.get("Description", "N/A")
                ),
                "N/A"
            ),
        )

        vulnerabilities.append(vuln.model_dump())

    return vulnerabilities


def parse_xlsx(file_path: str):
    df = pd.read_excel(file_path)

    vulnerabilities = []

    for index, (_, row) in enumerate(df.iterrows(), start=1):

        vuln = VulnerabilityModel(
            vulnerability_id=f"VULN-{index:03d}",

            title=clean_value(
                row.get(
                    "title",
                    row.get(
                        "Name",
                        row.get("Plugin Name", "Unknown")
                    )
                ),
                "Unknown"
            ),

            cve=clean_value(
                row.get(
                    "cve",
                    row.get("CVE", "N/A")
                ),
                "N/A"
            ),

            severity=clean_value(
                row.get(
                    "severity",
                    row.get("Severity", "Unknown")
                ),
                "Unknown"
            ),

            host=clean_value(
                row.get(
                    "host",
                    row.get(
                        "Host",
                        row.get("IP Address", "Unknown")
                    )
                ),
                "Unknown"
            ),

            description=clean_value(
                row.get(
                    "description",
                    row.get("Description", "N/A")
                ),
                "N/A"
            ),
        )

        vulnerabilities.append(vuln.model_dump())

    return vulnerabilities