import pytest
from ingest import chunk_text, detect_framework, normalize_text

def test_detect_nist_framework() -> None:
    assert detect_framework("NIST_CSF_2.0.pdf") == "NIST"

def test_detect_cis_framework() -> None:
    assert detect_framework("CIS_Controls_v8.1.pdf") == "CIS"

def test_detect_iso_framework() -> None:
    assert detect_framework("ISO_27001_2022.pdf") == "ISO27001"

def test_unknown_framework() -> None:
    assert detect_framework("company_policy.pdf") == "OTHER"

def test_normalize_text() -> None:
    text = "First    line\n\n\nSecond line"
    assert normalize_text(text) == "First line\n\nSecond line"

def test_empty_text_returns_no_chunks() -> None:
    assert chunk_text("   ") == []

def test_long_text_creates_multiple_chunks() -> None:
    text = " ".join(f"word{i}" for i in range(1000))
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 1
    assert all(len(chunk) <= 300 for chunk in chunks)

def test_invalid_chunk_size() -> None:
    with pytest.raises(ValueError):
        chunk_text("sample text", chunk_size=100, overlap=10)

def test_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text("sample text", chunk_size=200, overlap=200)