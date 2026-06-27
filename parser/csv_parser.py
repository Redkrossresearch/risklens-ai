import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import VulnerabilityModel


def parse_csv(file_path):
    """
    Reads a CSV file and returns a list of VulnerabilityModel objects.
    """

    df = pd.read_csv(file_path)

    vulnerabilities = []

    for index, row in df.iterrows():

        vulnerability = VulnerabilityModel(
            vulnerability_id=f"VULN-{index + 1:03}",
            title=row["Title"],
            cve=row["CVE"],
            severity=row["Severity"],
            host=row["Host"],
            description=row["Description"]
        )

        vulnerabilities.append(vulnerability)

    return vulnerabilities


if __name__ == "__main__":

    vulnerabilities = parse_csv("samples/sample.csv")

    for vulnerability in vulnerabilities:
        print(vulnerability.model_dump())