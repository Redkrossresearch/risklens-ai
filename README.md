# RiskLens ChromaDB starter

This is a local-development compliance search service. It stores starter ISO,
NIST, and CIS control text in a persistent Chroma collection.

## 1. Create and activate a virtual environment

From PowerShell:

```powershell
cd risklens_chromadb
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use the virtual environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Configure a fresh secret

Generate a secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy that value and set it only for the current PowerShell session:

```powershell
$env:RISKLENS_SHARED_SECRET = "paste-the-new-random-value-here"
```

Do not reuse `RiskLensSecureToken2026`; it has been exposed. Do not place the new
secret in Python files, Git, screenshots, tickets, or ordinary application logs.

## 3. Run the service smoke test

```powershell
python risklens_db.py
```

On the first run, Chroma's default local embedding model may need to download.
The database is created under `compliance_db/` and is excluded from Git.

## 4. Run security-focused unit tests

```powershell
python -m pytest -q
```

## Backend integration

Import `SecureComplianceDatabase`, create one long-lived instance during backend
startup, and call `secure_query`. Do not create a client for every request.

```python
from risklens_db import SecureComplianceDatabase

database = SecureComplianceDatabase(db_path="./compliance_db")

result = database.secure_query(
    user_token=request_token,
    raw_finding="Inactive accounts are not being removed.",
    n_results=3,
)
```

The backend must additionally provide TLS, rate limiting, structured audit logs,
authorization, and secret rotation. A static shared secret is only a prototype
control, not sufficient production identity management.

## Production note

Chroma documents `PersistentClient` as a local development/testing client. Use a
server-backed deployment with authentication, TLS, backups, restricted network
access, and a documented retention policy for production.
