# FileSure — Tech Operations Intern Assignment

A full-stack pipeline: CSV → MongoDB → Node.js API → HTML frontend.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| MongoDB | 6+ (running locally on port 27017) |

---

## Project Structure

```
filesure-project/
├── ingestion/
│   ├── ingest.py            # Python data cleaning + MongoDB loader
│   ├── requirements.txt
│   └── company_records.csv  # <-- place the CSV here
├── api/
│   ├── index.js             # Express API
│   └── package.json
└── frontend/
    └── index.html           # Single-page UI
```

---

## Setup

### 1. Start MongoDB

```bash
mongod --dbpath /usr/local/var/mongodb   # macOS Homebrew
# or
sudo systemctl start mongod              # Linux
```

### 2. Run the Python ingestion script

```bash
cd ingestion
pip install -r requirements.txt
cp /path/to/company_records.csv .
python ingest.py
```

Expected output:
```
✓ Ingestion complete
  Total records inserted : 80
  Missing CIN            : 5
  Invalid CIN format     : 0
  Flagged emails         : 7
  Collection             : filesure.companies
```

### 3. Start the API

```bash
cd ../api
npm install
node index.js
# → API running on http://localhost:3000
```

### 4. Open the frontend

Open `frontend/index.html` directly in your browser (no build step needed).

---

## API Reference

### `GET /companies`

Returns paginated company records.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | string | — | Filter by status (case-insensitive). E.g. `Active` |
| `state` | string | — | Filter by state. E.g. `Maharashtra` |
| `page` | int | 1 | Page number |
| `limit` | int | 20 | Records per page (max 100) |

**Example:**
```
GET /companies?status=Active&state=Maharashtra&page=1&limit=10
```

**Response:**
```json
{
  "page": 1,
  "limit": 10,
  "total": 4,
  "totalPages": 1,
  "data": [...]
}
```

---

### `GET /companies/summary`

Returns record counts grouped by status.

**Response:**
```json
{
  "total": 80,
  "breakdown": [
    { "status": "Active", "count": 28 },
    { "status": "Strike Off", "count": 20 },
    ...
  ]
}
```

---

## Data Cleaning Decisions

| Issue | Decision |
|-------|----------|
| Mixed date formats (DD-MM-YYYY, MM/DD/YYYY, YYYY/MM/DD) | Try all three formats in sequence; store as BSON Date |
| paid_up_capital with ₹, Rs., commas | Strip all non-digit characters; store as integer |
| Inconsistent status casing (ACTIVE, active, Active) | Normalise to title-case via a lookup table |
| Invalid emails (@@, double dots, spaces) | Flag with `email_valid: false`; keep the record |
| Missing CIN | Store as `null`; flag with `cin_valid: false` |
| Blank director_2 | Stored as `null` — not an error |

---

## MongoDB Indexes

```js
// 1. Sparse unique-ish index on CIN — primary lookup for the API
db.companies.createIndex({ cin: 1 }, { sparse: true })

// 2. Compound index on (status, state) — backs the filter query
db.companies.createIndex({ status: 1, state: 1 })
```

The compound index means `GET /companies?status=Active&state=Maharashtra`
performs an index scan rather than a full collection scan.

---