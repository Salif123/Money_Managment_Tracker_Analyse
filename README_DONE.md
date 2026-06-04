# Bill Manager - Database Models & Migrations Complete

Welcome to **Bill Manager**, a local bill and invoice manager app designed to extract, store, and manage your billing transactions. This documentation covers the complete setup for both **Section 1 (App Scaffolding)** and **Section 2 (Database Models, Migrations, & API endpoints)**.

---

## What is Built

### 1. Python 3.11 Backend (FastAPI)
- **Settings & Config**: Configured with `pydantic-settings` to load environments (`.env`).
- **Database Engine (`backend/database.py`)**: Configured SQLAlchemy with SQLite support (`check_same_thread=False` parameter). Exposes a `get_db` dependency for database sessions.
- **SQLAlchemy Schemas (`backend/models.py`)**:
  - **`Vendor`**: Stores vendor metadata (name, address, email, phone, GSTIN, PAN).
  - **`Invoice`**: Tracks invoice headers, totals, file paths, extraction method, notes, and soft-delete timestamp (`deleted_at`).
  - **`LineItem`**: Details line-by-line descriptions, HSN codes, quantity, unit, price, CGST, SGST, and IGST percentages.
  - **`TaxEntry`**: Tracks individual tax breakdown totals (CGST, SGST, IGST, CESS, etc.) and rates.
  - **`Category`**: Custom categorization tags with names and hex colors.
  - **`InvoiceCategory`**: Many-to-many relationship mapping invoices to categories.
- **Alembic Migrations**:
  - Configured project migrations (`alembic.ini`, `alembic/env.py`) to dynamically pull settings from the application environment variables.
  - Created initial schema migration script `alembic/versions/0001_initial.py`.
- **CRUD Query Logic (`backend/crud/`)**:
  - `vendors.py`: alphabetized lookup, automated creation, profile backfill.
  - `invoices.py`: creates parent invoice record with children (line items, tax entries, categories), handles soft-deletes, details retrieval, and text search on numbers, notes, and vendor names.
- **API Routers**:
  - `health.py`: GET `/api/health` → checks system health.
  - `invoices.py`:
    - `GET /api/invoices`: Returns list of active (non soft-deleted) invoices. Supports query parameters `vendor_id`, `date_from`, `date_to`, and `search`.
    - `GET /api/invoices/{id}`: Returns single active invoice with all details, line items, and tax entries.
    - `DELETE /api/invoices/{id}`: Performs a soft-delete (marks `deleted_at` timestamp).
    - `PATCH /api/invoices/{id}/notes`: Modifies the invoice text notes field.

### 2. React 18 Frontend (Vite + Tailwind CSS)
- **Vite Proxy Config**: Maps `/api` to the backend running on `http://localhost:8000`.
- **Styling**: Configured with Tailwind CSS v3 including the `@tailwindcss/forms` plugin.
- **Dashboard Workspace**: Beautiful dark-themed sidebar, active navigation, and live API diagnostic health checks.

### 3. Storage & Assets Scaffold
- **Storage Target**: Files are uploaded and statically served via `uploads/` mount.
- **Git Rules**: `.gitignore` configured to exclude local sqlite database files, python virtual environment files, node packages, and environment secrets.

---

## Folder Structure

```text
bill-manager/
├── backend/
│   ├── alembic/                 # Alembic migration scripts and environment
│   │   ├── env.py               # Configures metadata and DATABASE_URL
│   │   └── versions/            # Database schema versions history
│   │       └── 0001_initial.py  # Section 2: Initial tables schema
│   ├── crud/                    # Section 2: Database query helper files
│   │   ├── invoices.py          # Invoice retrieval, create, search, and delete
│   │   └── vendors.py           # Vendor retrieval and lookup logic
│   ├── routers/                 # FastAPI routes definitions
│   │   ├── health.py            # Status verification
│   │   └── invoices.py          # Section 2: GET, DELETE, PATCH invoice routes
│   ├── alembic.ini              # Alembic environment config
│   ├── config.py                # App settings loader (Pydantic Settings)
│   ├── database.py              # Section 2: DB engine & sessionmaker config
│   ├── main.py                  # API endpoints mount & static folder service
│   ├── models.py                # Section 2: All SQLAlchemy database models
│   ├── requirements.txt         # Backend Python dependencies list
│   └── .env                     # Local configuration secrets (gitignored)
├── frontend/
│   ├── package.json             # NPM package scripts & configuration
│   ├── vite.config.js           # Proxy maps frontend requests to API
│   ├── src/
│   │   ├── App.jsx              # Workspace Dashboard UI
│   │   └── index.css            # Tailwind directives
│   └── ...                      # Configurations for build, PostCSS, and tailwind
├── uploads/                     # Storage folder for uploaded invoices (gitignored)
├── .gitignore                   # Exclude list for git commits
└── README_DONE.md               # Summary of Section 1 & 2 additions
```

---

## Environment Variables List

The backend loads config variables from `.env` inside `backend/`:

| Key | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./bill_manager.db` | Connection string to SQLite database file |
| `UPLOAD_DIR` | `../uploads` | Storage directory for original invoice documents |
| `SECRET_KEY` | `changeme` | Secret key for hashing security functions |

---

## How to Run

### 1. Database Migrations Setup
Run this once to configure your local SQLite database structure. From the `backend/` directory:
```bash
# Activate your virtual environment:
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# Execute Alembic migrations
alembic upgrade head
```

### 2. Run Backend (FastAPI API Server)
From the `backend/` directory with the virtual environment active:
```bash
uvicorn main:app --reload --port 8000
```
*The API will start on [http://localhost:8000](http://localhost:8000).*

### 3. Run Frontend (React Dashboard)
From the `frontend/` directory in a new terminal window:
```bash
# Install NPM packages (first run only)
npm install

# Start Vite server
npm run dev
```
*The UI will start on [http://localhost:5173](http://localhost:5173).*

---

## API Verification Cheatsheet

With the Uvicorn server running, verify database endpoints with these client commands:

### List Invoices (GET)
```bash
curl -i http://localhost:8000/api/invoices
```
*Returns `[]` initially. Filters supported: `?vendor_id=...`, `?date_from=2026-06-01`, `?date_to=2026-06-30`, `?search=ACME`.*

### Get Invoice Details (GET)
```bash
curl -i http://localhost:8000/api/invoices/{uuid}
```

### Update Notes (PATCH)
```bash
curl -i -X PATCH -H "Content-Type: application/json" -d '{"notes": "Revised item total checks"}' http://localhost:8000/api/invoices/{uuid}/notes
```

### Soft-Delete Invoice (DELETE)
```bash
curl -i -X DELETE http://localhost:8000/api/invoices/{uuid}
```
*Removes invoice from list results by applying a `deleted_at` timestamp.*
