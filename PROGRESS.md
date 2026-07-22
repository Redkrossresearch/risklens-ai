# RiskLens AI — Backend Progress (Prasad)

## ✅ Confirmed Done
- Top 5 Risks empty bug fixed (main.py/upload.py data sync)
- Abhiya's Week 3-5 AI merge (Risk Score, structured JSON)
- User Auth — DB persistence (Supabase `users` table)
- Vulnerabilities — DB persistence (Supabase `vulnerabilities` table)
- Repo cleanup (venv, __pycache__ removed from git)
- compliance/ticket JSON columns added to `vulnerabilities` table (Supabase)
- compliance/ticket JSON data confirmed working end-to-end (tested with test2.csv, no errors)
- JWT auth gap fixed — upload endpoints now require login (401 without token, 200 with)
- Duplicate upload prevention (cve+host check) — confirmed working, response shows "duplicate_updated" field
- Connection stability (pool_pre_ping, pool_recycle)
- AI output validation/cleanup layer (Qwen3 1.7B patch)
- Confirmed only ONE upload.py exists (deleted stray duplicate outside project folder)
- Shubham's compliance/RAG module merged (api.py, ingest.py, rag_pipeline.py, risklens_db.py, compliance_report.py)
- Resolved merge conflicts: separated report_generator.py (PDF reports) from compliance_report.py (RAG compliance mapping)
- Abhiya's improved AI prompt rules merged (risk_rating validation, compliance control code format, "Not mapped" fallback)
- PDF upload fully implemented (pdfplumber table extraction + AI analysis + DB persistence)
- Real-world scanner format compatibility: tested with Nessus-format and Qualys-format sample CSVs
  (added column fallback mapping for Name/Risk/IP/CVE ID/Synopsis/Threat, Qualys numeric severity → text normalization)

## In Progress / Pending
- XLSX upload fully working (parsing, AI analysis, DB persistence) - fixed column header whitespace bug
- PDF download endpoints added (/report/executive/download, /report/technical/download) for Tanishka's frontend

## ❌ Not Done Yet
- AI model 14B test (currently 1.7B)

## Team Status
- Shubham: compliance module pending push
- Tanishka: branch checkout issue (main branch conflict) — being resolved
- Abhiya: venv + Week 3-5 merge — done

## Notes
- Multiple Claude chat sessions have been used for this project — same laptop/project folder,
  so code changes from one session are visible in another (files are shared, chats are not).
  ALWAYS verify actual file content via terminal commands before assuming something is/isn't done.