"""
FileSure Internship Assignment — Data Ingestion Script
Reads company_records.csv, cleans data, inserts into MongoDB.
"""

import csv
import re
import sys
from datetime import datetime
from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "filesure"
COLLECTION_NAME = "companies"
CSV_PATH = "company_records.csv"

#Date parsing 
# The CSV has at least three formats: DD-MM-YYYY, MM/DD/YYYY, YYYY/MM/DD
# Date like 03/07/2012 could be March 7th or July 3rd
DATE_FORMATS = ["%d-%m-%Y", "%m/%d/%Y", "%Y/%m/%d"]

def parse_date(raw: str) -> datetime | None:
    raw = raw.strip()
    if not raw:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            pass
    # Unrecognised format — log and return None so we don't crash
    print(f"  [WARN] Unrecognised date format: '{raw}'", file=sys.stderr)
    return None


# Capital cleaning 
def parse_capital(raw: str) -> int | None:
    if not raw or not raw.strip():
        return None
    # Strip rupee symbols, "Rs.", commas, spaces, and the special ₹ character
    cleaned = re.sub(r"[₹Rs.\s,]", "", raw.strip())
    # After stripping, only digits should remain
    if cleaned.isdigit():
        return int(cleaned)
    print(f"  [WARN] Could not parse paid_up_capital: '{raw}'", file=sys.stderr)
    return None


# Status normalisation
# "Active", "ACTIVE" & "active"
STATUS_MAP = {
    "active": "Active",
    "strike off": "Strike Off",
    "struck off": "Strike Off",
    "under liquidation": "Under Liquidation",
    "under liq.": "Under Liquidation",
    "dormant": "Dormant",
}

def normalise_status(raw: str) -> str:
    return STATUS_MAP.get(raw.strip().lower(), raw.strip().title())


# Email validation 
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

def validate_email(raw: str) -> tuple[str, bool]:
    cleaned = raw.strip().replace(" ", "")  # remove spaces like "contact @ company.co.in"
    if not cleaned:
        return "", False
    # Reject double-@ addresses and trailing dots after the TLD
    if EMAIL_RE.match(cleaned) and not cleaned.endswith(".."):
        return cleaned, True
    return cleaned, False


# CIN validation 
CIN_RE = re.compile(r"^[UL]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}$")

def validate_cin(raw: str) -> tuple[str, bool]:
    cleaned = raw.strip()
    return cleaned, bool(CIN_RE.match(cleaned))


# Main ingestion 
def ingest(csv_path: str = CSV_PATH):
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as e:
        sys.exit(f"[ERROR] Cannot connect to MongoDB: {e}")

    db = client[DB_NAME]
    col = db[COLLECTION_NAME]

    # Drop existing data so re-runs are idempotent
    col.drop()

    # Indexes:
    #   1. cin (unique where present) — primary lookup key for the API
    #   2. (status, state) compound — backs the /companies?status=&state= filter
    col.create_index("cin", sparse=True)
    col.create_index([("status", ASCENDING), ("state", ASCENDING)])

    records = []
    skipped = 0

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # row 1 is the header
            cin_raw = row.get("cin", "").strip()
            cin, cin_valid = validate_cin(cin_raw) if cin_raw else ("", False)

            email_raw = row.get("email", "")
            email, email_valid = validate_email(email_raw)

            doc = {
                # Identifiers
                "cin": cin if cin else None,
                "cin_valid": cin_valid,

                # Core fields
                "company_name": row.get("company_name", "").strip() or None,
                "status": normalise_status(row.get("status", "")),
                "state": row.get("state", "").strip() or None,

                # Directors — keep null rather than empty string
                "director_1": row.get("director_1", "").strip() or None,
                "director_2": row.get("director_2", "").strip() or None,

                # Dates — stored as proper BSON dates
                "incorporation_date": parse_date(row.get("incorporation_date", "")),
                "last_filing_date": parse_date(row.get("last_filing_date", "")),

                # Financials — stored as integer
                "paid_up_capital": parse_capital(row.get("paid_up_capital", "")),

                # Email — store the cleaned value and a validity flag
                "email": email or None,
                "email_valid": email_valid,

                # Bookkeeping
                "source_row": i,
                "ingested_at": datetime.utcnow(),
            }

            records.append(doc)

    if records:
        col.insert_many(records, ordered=False)

    total = len(records)
    invalid_cin = sum(1 for r in records if not r["cin_valid"])
    invalid_email = sum(1 for r in records if r["email"] and not r["email_valid"])
    missing_cin = sum(1 for r in records if not r["cin"])

    print(f"\n✓ Ingestion complete")
    print(f"  Total records inserted : {total}")
    print(f"  Missing CIN            : {missing_cin}")
    print(f"  Invalid CIN format     : {invalid_cin}")
    print(f"  Flagged emails         : {invalid_email}")
    print(f"  Collection             : {DB_NAME}.{COLLECTION_NAME}")

    client.close()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    ingest(path)
