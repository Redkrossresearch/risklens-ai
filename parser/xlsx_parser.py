import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import VulnerabilityModel
from parser.validator import validate_severity, validate_cve
from parser.logger_config import logger

def parse_xlsx(file_path):
    """
    Reads an Excel (.xlsx) file and returns a list of VulnerabilityModel objects.
    """

    try:
        # Read Excel
        df = pd.read_excel(file_path, engine="openpyxl")
        logger.info("Excel file loaded successfully.")

        required_columns = [
            "Title",
            "CVE",
            "Severity",
            "Host",
            "Description"
        ]

        missing_columns = [
            column for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            print(f"Missing columns: {missing_columns}")
            return []

    except FileNotFoundError:
        logger.error("Excel file not found.")
        print("Excel file not found.")
        return []

    except Exception as e:
        logger.error(str(e))
        print(e)
        return []

    vulnerabilities = []
    seen_cves = set()

    for index, row in df.iterrows():

        if (
            pd.isna(row["Title"]) or
            pd.isna(row["CVE"]) or
            pd.isna(row["Severity"]) or
            pd.isna(row["Host"]) or
            pd.isna(row["Description"])
        ):
            logger.warning(f"Missing data in row {index + 2}")
            print(f"Skipping row {index + 2}: Missing required data")
            continue

        if not validate_severity(row["Severity"]):
            logger.warning(f"Invalid Severity in row {index + 2}")
            print(f"Skipping row {index + 2}: Invalid Severity")
            continue

        if not validate_cve(row["CVE"]):
            logger.warning(f"Invalid CVE in row {index + 2}")
            print(f"Skipping row {index + 2}: Invalid CVE")
            continue

        if row["CVE"] in seen_cves:
            logger.warning(f"Duplicate CVE found: {row['CVE']}")
            print(f"Skipping row {index + 2}: Duplicate CVE")
            continue

        seen_cves.add(row["CVE"])

        vulnerability = VulnerabilityModel(
            vulnerability_id=f"VULN-{index + 1:03}",
            title=row["Title"],
            cve=row["CVE"],
            severity=row["Severity"],
            host=row["Host"],
            description=row["Description"]
        )

        vulnerabilities.append(vulnerability)

    print("\n========== XLSX Parsing Summary ==========")
    print(f"Total Rows    : {len(df)}")
    print(f"Valid Records : {len(vulnerabilities)}")
    print(f"Rejected Rows : {len(df) - len(vulnerabilities)}")

    logger.info("XLSX Parsing Completed")

    return vulnerabilities


if __name__ == "__main__":

    file_name = input("Enter Excel file name: ")

    vulnerabilities = parse_xlsx(f"samples/{file_name}")

    for vulnerability in vulnerabilities:
        print(vulnerability.model_dump())