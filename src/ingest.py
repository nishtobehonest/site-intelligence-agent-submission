"""
ingest.py
---------
Loads raw documents from data/raw/, chunks them, embeds them,
and indexes them into Chroma vector store.

HVAC collections (Phase 1):
  - osha         : OSHA field documentation
  - manuals      : Equipment maintenance manuals
  - job_history  : Synthetic job history records

Drone collections (Phase 2):
  - inspection_records  : Drone anomaly records with spatial metadata
  - historical_baselines: Zone/equipment normal baselines
  - compliance_docs     : OSHA standards for drone inspection domain

Run this once after adding new documents to data/raw/.
Usage:
  python src/ingest.py                  # HVAC domain (Phase 1)
  python src/ingest.py --domain drone   # Drone domain (Phase 2)
  python src/ingest.py --domain all     # Both domains
"""

import os
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

HVAC_SOURCES = {
    "osha": "./data/raw/osha",
    "manuals": "./data/raw/manuals",
    "job_history": "./data/raw/job_history",
}

DRONE_SOURCES = {
    "inspection_records": "./data/raw/drone",
    "historical_baselines": "./data/raw/drone",
    "compliance_docs": "./data/raw/drone",
}

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def load_pdf_and_txt(source_dir: str) -> list[Document]:
    docs = []
    path = Path(source_dir)
    if not path.exists():
        print(f"  [SKIP] Directory not found: {source_dir}")
        return docs

    for file in path.rglob("*.pdf"):
        try:
            loader = PyPDFLoader(str(file))
            docs.extend(loader.load())
            print(f"  [OK] Loaded PDF: {file.name}")
        except Exception as e:
            print(f"  [ERR] Failed to load {file.name}: {e}")

    for file in path.rglob("*.txt"):
        try:
            loader = TextLoader(str(file))
            docs.extend(loader.load())
            print(f"  [OK] Loaded TXT: {file.name}")
        except Exception as e:
            print(f"  [ERR] Failed to load {file.name}: {e}")

    return docs


def load_hvac_job_history(source_dir: str) -> list[Document]:
    docs = []
    path = Path(source_dir)
    for file in path.rglob("*.json"):
        try:
            with open(file) as f:
                records = json.load(f)
            for record in records:
                content = json.dumps(record)
                metadata = {"source": str(file), "job_id": record.get("job_id", "unknown")}
                docs.append(Document(page_content=content, metadata=metadata))
            print(f"  [OK] Loaded JSON: {file.name} ({len(records)} records)")
        except Exception as e:
            print(f"  [ERR] Failed to load {file.name}: {e}")
    return docs


def load_inspection_records(source_dir: str) -> list[Document]:
    docs = []
    json_file = Path(source_dir) / "inspection_records.json"
    if not json_file.exists():
        print(f"  [SKIP] Not found: {json_file}")
        return docs
    with open(json_file) as f:
        records = json.load(f)
    for record in records:
        content = (
            f"Inspection Record {record['record_id']} | "
            f"Site: {record['site_id']} | Zone: {record['zone_id']} | "
            f"Date: {record['flight_date']} | Equipment: {record['equipment_type']} | "
            f"Anomaly: {record['anomaly_type']} | Severity: {record['severity']}\n\n"
            f"{record['inspector_notes']}\n\n"
            f"Resolution status: {record['resolution_status']}. "
            f"Compliance flag: {record['compliance_flag']}."
        )
        # Store flight_date as both string (human-readable) and int (YYYYMMDD)
        # Chroma's $gte/$lte operators require numeric types for comparison.
        flight_date_int = int(record["flight_date"].replace("-", ""))
        metadata = {
            "source": str(json_file),
            "record_id": record["record_id"],
            "zone_id": record["zone_id"],
            "flight_date": record["flight_date"],
            "flight_date_int": flight_date_int,
            "severity": record["severity"],
            "site_id": record["site_id"],
            "equipment_type": record["equipment_type"],
        }
        docs.append(Document(page_content=content, metadata=metadata))
    print(f"  [OK] Loaded inspection_records.json ({len(records)} records)")
    return docs


def load_historical_baselines(source_dir: str) -> list[Document]:
    docs = []
    json_file = Path(source_dir) / "historical_baselines.json"
    if not json_file.exists():
        print(f"  [SKIP] Not found: {json_file}")
        return docs
    with open(json_file) as f:
        records = json.load(f)
    for record in records:
        content = (
            f"Historical Baseline {record['baseline_id']} | "
            f"Zone: {record['zone_id']} | Equipment: {record['equipment_type']}\n\n"
            f"Normal temperature range: {record['normal_temperature_range']}. "
            f"Typical anomaly rate: {record['typical_anomaly_rate']}. "
            f"Last major maintenance: {record['last_major_maintenance']}.\n\n"
            f"{record['baseline_notes']}"
        )
        metadata = {
            "source": str(json_file),
            "baseline_id": record["baseline_id"],
            "zone_id": record["zone_id"],
            "equipment_type": record["equipment_type"],
        }
        docs.append(Document(page_content=content, metadata=metadata))
    print(f"  [OK] Loaded historical_baselines.json ({len(records)} records)")
    return docs


def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(docs)


def ingest_collection(collection_name: str, docs: list[Document], embeddings):
    if not docs:
        print(f"  [WARN] No documents for {collection_name}. Skipping.")
        return None

    chunks = chunk_documents(docs)
    print(f"  [OK] {len(docs)} documents -> {len(chunks)} chunks")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=CHROMA_PERSIST_DIR
    )
    print(f"  [OK] Indexed into Chroma collection: {collection_name}")
    return vectorstore


def ingest_hvac(embeddings):
    print("\n=== Ingesting HVAC domain (Phase 1) ===")
    for collection_name, source_dir in HVAC_SOURCES.items():
        print(f"\n--- {collection_name} ---")
        if collection_name == "job_history":
            docs = load_hvac_job_history(source_dir)
        else:
            docs = load_pdf_and_txt(source_dir)
        ingest_collection(collection_name, docs, embeddings)


def ingest_drone(embeddings):
    print("\n=== Ingesting Drone domain (Phase 2) ===")

    print("\n--- inspection_records ---")
    docs = load_inspection_records(DRONE_SOURCES["inspection_records"])
    ingest_collection("inspection_records", docs, embeddings)

    print("\n--- historical_baselines ---")
    docs = load_historical_baselines(DRONE_SOURCES["historical_baselines"])
    ingest_collection("historical_baselines", docs, embeddings)

    print("\n--- compliance_docs ---")
    docs = load_pdf_and_txt(DRONE_SOURCES["compliance_docs"])
    # Filter out JSON files already loaded above — PDFs only for compliance_docs
    ingest_collection("compliance_docs", docs, embeddings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--domain",
        choices=["hvac", "drone", "all"],
        default="hvac",
        help="Which domain to ingest (default: hvac)"
    )
    args = parser.parse_args()

    print("=== Site Intelligence Agent: Document Ingestion ===")
    embeddings = get_embeddings()

    if args.domain in ("hvac", "all"):
        ingest_hvac(embeddings)

    if args.domain in ("drone", "all"):
        ingest_drone(embeddings)

    print("\n=== Ingestion complete. ===")


if __name__ == "__main__":
    main()
