import hashlib
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import VulnerabilityModel
from parser.validator import validate_severity, validate_cve
from parser.logger_config import logger

def generate_stable_id(title, cve, host):
    raw = f"{title}:{cve}:{host}".lower().strip()
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def parse_csv(file_path):
    """
    Reads a CSV file and returns a list of VulnerabilityModel objects.
    """

    try:
        # Read CSV
        df = pd.read_csv(file_path)
        logger.info("CSV file loaded successfully.")

        # Validate required columns
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
        logger.error("CSV file not found.")
        print("CSV file not found.")
        return []

    except pd.errors.EmptyDataError:
        logger.error("CSV file is empty.")
        print("CSV file is empty.")
        return []

    except Exception as e:
        logger.error(str(e))
        print(e)
        return []

    vulnerabilities = []
    seen_cves = set()

    for index, row in df.iterrows():

        # Check for missing values
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

        # Validate Severity
        if not validate_severity(row["Severity"]):
            logger.warning(f"Invalid Severity in row {index + 2}")
            print(f"Skipping row {index + 2}: Invalid Severity")
            continue

        # Validate CVE
        if not validate_cve(row["CVE"]):
            logger.warning(f"Invalid CVE in row {index + 2}")
            print(f"Skipping row {index + 2}: Invalid CVE")
            continue

        # Check duplicate CVEs
        if row["CVE"] in seen_cves:
            logger.warning(f"Duplicate CVE found: {row['CVE']}")
            print(f"Skipping row {index + 2}: Duplicate CVE")
            continue

        seen_cves.add(row["CVE"])

        vulnerability = VulnerabilityModel(
            vulnerability_id=generate_stable_id(
                row["Title"],
                row["CVE"],
                row["Host"]
            ),
            title=row["Title"],
            cve=row["CVE"],
            severity=row["Severity"],
            host=row["Host"],
            description=row["Description"]
        )

        vulnerabilities.append(vulnerability)

    print("\n========== Parsing Summary ==========")
    print(f"Total Rows    : {len(df)}")
    print(f"Valid Records : {len(vulnerabilities)}")
    print(f"Rejected Rows : {len(df) - len(vulnerabilities)}")

    logger.info("CSV Parsing Completed")

    return vulnerabilities


if __name__ == "__main__":

    file_name = input("Enter CSV file name: ")

    vulnerabilities = parse_csv(f"samples/{file_name}")

    for vulnerability in vulnerabilities:
        print(vulnerability.model_dump())