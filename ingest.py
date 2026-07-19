"""Extract, chunk, and load compliance documents into ChromaDB."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Iterator

import chromadb
from pypdf import PdfReader


# ==========================================
# CONFIG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR / "source_docs"
DATABASE_PATH = BASE_DIR / "compliance_db"

COLLECTION_NAME = "frameworks"
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
BATCH_SIZE = 50

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


# ==========================================
# TEXT HELPERS
# ==========================================

def normalize_text(text: str) -> str:
    """Clean extracted text while preserving useful paragraph structure."""

    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks."""

    if chunk_size < 200:
        raise ValueError("chunk_size must be at least 200")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    text = normalize_text(text)

    if not text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        proposed_end = min(start + chunk_size, len(text))
        end = proposed_end

        if proposed_end < len(text):
            search_start = start + chunk_size // 2

            boundaries = [
                text.rfind("\n\n", search_start, proposed_end),
                text.rfind(". ", search_start, proposed_end),
                text.rfind(" ", search_start, proposed_end),
            ]

            boundary = max(boundaries)

            if boundary > start:
                end = boundary + 1

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(start + 1, end - overlap)

    return chunks


# ==========================================
# DOCUMENT METADATA HELPERS
# ==========================================

def calculate_file_sha256(path: Path) -> str:
    """Calculate SHA-256 hash for source document integrity tracking."""

    sha256 = hashlib.sha256()

    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def detect_framework(filename: str) -> str:
    """Detect compliance framework from filename."""

    name = filename.lower()

    if "nist" in name or "csf" in name:
        return "NIST"

    if "cis" in name:
        return "CIS"

    if "iso" in name or "27001" in name:
        return "ISO27001"

    return "OTHER"


def detect_document_version(filename: str) -> str:
    """Detect rough framework version from filename."""

    name = filename.lower()

    if "2.0" in name or "cswp.29" in name:
        return "2.0"

    if "8.1" in name or "v8.1" in name:
        return "8.1"

    if "8" in name or "v8" in name:
        return "8"

    if "2022" in name:
        return "2022"

    return "UNKNOWN"


def extract_control_id(text: str, framework: str) -> str:
    """Try to extract control/control-like ID from a text chunk."""

    clean_text = " ".join(text.split())

    patterns_by_framework = {
        "NIST": [
            r"\b(?:GV|ID|PR|DE|RS|RC)\.[A-Z]{2}-\d{2}\b",
            r"\b(?:PR|ID|DE|RS|RC)\.[A-Z]{2}-\d+\b",
        ],
        "CIS": [
            r"\bSafeguard\s+\d+(?:\.\d+)?\b",
            r"\bControl\s+\d+(?:\.\d+)?\b",
            r"\bCIS\s+Control\s+\d+(?:\.\d+)?\b",
        ],
        "ISO27001": [
            r"\bA\.\d+(?:\.\d+){1,3}\b",
            r"\b\d+(?:\.\d+){1,3}\b",
        ],
    }

    patterns = patterns_by_framework.get(framework, [])

    for pattern in patterns:
        match = re.search(pattern, clean_text, flags=re.IGNORECASE)
        if match:
            return match.group(0)

    return "N/A"


# ==========================================
# EXTRACTION
# ==========================================

def extract_pages(path: Path) -> Iterator[tuple[int, str]]:
    """Extract text from PDF/TXT/MD with page numbers."""

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        reader = PdfReader(path)

        if reader.is_encrypted:
            raise ValueError(f"Encrypted PDF is not supported: {path.name}")

        for page_number, page in enumerate(reader.pages, start=1):
            text = normalize_text(page.extract_text() or "")

            if text:
                yield page_number, text

        return

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")

    text = normalize_text(text)

    if text:
        yield 1, text


def create_chunk_id(
    filename: str,
    file_sha256: str,
    page_number: int,
    chunk_number: int,
    text: str,
) -> str:
    """Create stable chunk ID."""

    value = (
        f"{filename}|{file_sha256}|{page_number}|{chunk_number}|{text}"
    ).encode("utf-8")

    return hashlib.sha256(value).hexdigest()


# ==========================================
# INGESTION
# ==========================================

def safe_delete_existing_file_chunks(collection: Any, source_file: str) -> None:
    """Delete old chunks from same file before re-ingesting."""

    try:
        collection.delete(where={"source_file": source_file})
    except Exception:
        # If no matching records exist, continue safely.
        pass


def ingest_file(collection: Any, path: Path) -> int:
    """Chunk and load one compliance document into ChromaDB."""

    file_size = path.stat().st_size

    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds 50 MB limit: {path.name}")

    framework = detect_framework(path.name)
    document_version = detect_document_version(path.name)
    file_sha256 = calculate_file_sha256(path)

    safe_delete_existing_file_chunks(collection, path.name)

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str | int]] = []

    for page_number, page_text in extract_pages(path):
        chunks = chunk_text(page_text)

        for chunk_number, chunk in enumerate(chunks, start=1):
            control_id = extract_control_id(chunk, framework)

            ids.append(
                create_chunk_id(
                    filename=path.name,
                    file_sha256=file_sha256,
                    page_number=page_number,
                    chunk_number=chunk_number,
                    text=chunk,
                )
            )

            documents.append(chunk)

            metadatas.append(
                {
                    "framework": framework,
                    "control_id": control_id,
                    "source_file": path.name,
                    "source_type": path.suffix.lower().replace(".", ""),
                    "document_version": document_version,
                    "file_sha256": file_sha256,
                    "page": page_number,
                    "chunk_number": chunk_number,
                    "chunk_size": len(chunk),
                }
            )

    for start in range(0, len(ids), BATCH_SIZE):
        collection.upsert(
            ids=ids[start : start + BATCH_SIZE],
            documents=documents[start : start + BATCH_SIZE],
            metadatas=metadatas[start : start + BATCH_SIZE],
        )

    return len(ids)


def main() -> None:
    """Load all supported compliance documents from source_docs."""

    DOCUMENTS_DIR.mkdir(exist_ok=True)

    files = sorted(
        path
        for path in DOCUMENTS_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and path.name.lower() != "readme.md"
    )

    if not files:
        print("No documents found.")
        print(f"Place PDF, TXT, or MD files inside: {DOCUMENTS_DIR}")
        return

    client = chromadb.PersistentClient(path=str(DATABASE_PATH))

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "RiskLens compliance framework controls"},
    )

    print("Starting compliance document ingestion...")

    total_chunks = 0

    for path in files:
        try:
            chunk_count = ingest_file(collection, path)
            total_chunks += chunk_count

            print(
                f"Loaded {path.name}: "
                f"{chunk_count} chunks "
                f"({detect_framework(path.name)}, version {detect_document_version(path.name)})"
            )

        except Exception as error:
            print(f"Failed {path.name}: {error}")

    print(f"Ingestion complete. Total new chunks: {total_chunks}")
    print(f"Total database records: {collection.count()}")


if __name__ == "__main__":
    main()