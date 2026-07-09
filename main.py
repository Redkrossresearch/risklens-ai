import os

from parser.csv_parser import parse_csv
from parser.xlsx_parser import parse_xlsx
from parser.pdf_parser import parse_pdf


def main():

    print("=" * 40)
    print("RiskLens AI Vulnerability Parser")
    print("=" * 40)

    file_name = input("Enter file name: ")

    extension = os.path.splitext(file_name)[1].lower()

    file_path = f"samples/{file_name}"

    if extension == ".csv":
        vulnerabilities = parse_csv(file_path)

    elif extension == ".xlsx":
        vulnerabilities = parse_xlsx(file_path)

    elif extension == ".pdf":
        vulnerabilities = parse_pdf(file_path)

    else:
        print("Unsupported file format.")
        return

    print("\n========== Parsed Vulnerabilities ==========\n")

    for vulnerability in vulnerabilities:
        print(vulnerability.model_dump())


if __name__ == "__main__":
    main()