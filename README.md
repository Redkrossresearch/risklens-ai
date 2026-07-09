# RiskLens AI - Vulnerability Parser

## Project Overview

The Vulnerability Parser module is a part of the RiskLens AI project. It reads vulnerability reports from multiple file formats and converts them into a standardized `VulnerabilityModel` for further risk assessment and compliance analysis.

## Features

- Parse CSV vulnerability reports
- Parse Excel (.xlsx) vulnerability reports
- Parse PDF vulnerability reports
- Validate CVE format
- Validate Severity values
- Detect duplicate CVEs
- Handle missing data
- Automatic parser selection using `main.py`

## Project Structure

```
risklens-ai/
│
├── parser/
│   ├── csv_parser.py
│   ├── xlsx_parser.py
│   ├── pdf_parser.py
│   ├── validator.py
│   └── logger_config.py
│
├── samples/
│   ├── sample.csv
│   ├── sample.xlsx
│   ├── sample.pdf
│
├── models.py
├── main.py
└── README.md
```

## Requirements

Install the required packages:

```bash
pip install pandas openpyxl pdfplumber pydantic
```

## How to Run

Run the application:

```bash
python main.py
```

Enter the file name when prompted:

```
sample.csv
```

or

```
sample.xlsx
```

or

```
sample.pdf
```

## Validation Rules

- CVE must follow the format:

```
CVE-YYYY-NNNN
```

Example:

```
CVE-2025-1234
```

- Allowed Severity values:
  - Critical
  - High
  - Medium
  - Low
  - Informational

## Sample Output

```
========== Parsing Summary ==========
Total Rows    : 3
Valid Records : 3
Rejected Rows : 0
```

## Technologies Used

- Python 3
- Pandas
- OpenPyXL
- PDFPlumber
- Pydantic

## Author

**Juveriya Sayed**

Cybersecurity Intern