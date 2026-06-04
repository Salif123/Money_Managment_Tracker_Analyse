# Bill Manager - Section 1 Complete

Welcome to **Bill Manager**, a local bill and invoice manager app designed to extract, store, and manage your billing transactions. Section 1 covers the baseline folder structure, configurations, and environment scaffolding.

---

## What is Built

1. **Python 3.11 Backend (FastAPI)**:
   - Configured with `pydantic-settings` to load settings from an environment configuration.
   - Built a `/api/health` status check endpoint.
   - Mounted static directory serving files from the `uploads/` directory.
   - Enabled CORS policies specifically allowing requests from the frontend client development origin (`http://localhost:5173`).
2. **React 18 Frontend (Vite + Tailwind CSS)**:
   - Configured Vite server proxy to map `/api` to the backend running on `http://localhost:8000`.
   - Setup Tailwind CSS v3 including the `@tailwindcss/forms` plugin for streamlined form stylings.
   - Built a premium dashboard workspace shell with a dark-themed sidebar, active-state routing, and real-time backend connection health monitoring.
3. **Storage & Assets Scaffold**:
   - Initialized an `uploads/` directory to hold processed files.
   - Created Git configuration rules (`.gitignore`) to ignore dependency directories (`node_modules`, `venv`), builds, local secrets (`.env`), and runtime file artifacts.

---

## Folder Structure

```text
bill-manager/
├── backend/
│   ├── main.py                  # FastAPI app entry point (CORS + routing)
│   ├── config.py                # App settings (Pydantic Settings loader)
│   ├── requirements.txt         # Backend Python dependencies
│   ├── .env                     # Local active env configurations (gitignored)
│   ├── .env.example             # Template env configuration file
│   └── routers/
│       └── health.py            # GET /health → {"status": "ok"}
├── frontend/
│   ├── package.json             # Frontend NPM scripts & dependencies
│   ├── vite.config.js           # Vite development server settings with /api proxy
│   ├── tailwind.config.js       # Tailwind CSS v3 theme rules
│   ├── postcss.config.js        # PostCSS build tool settings
│   ├── index.html               # Main entry HTML (imports Inter & Outfit typography)
│   └── src/
│       ├── main.jsx             # React DOM loader
│       ├── App.jsx              # Responsive dashboard shell and API diagnostics
│       └── index.css            # Tailwind CSS directives & scrollbar styles
├── uploads/                     # Storage target folder for uploaded bills (gitignored)
├── .gitignore                   # Workspace Git track exclusion rules
└── README_DONE.md               # Section 1 summary and instructions
```

---

## How to Run

Follow these commands to start the development servers.

### Backend (FastAPI)
From the `bill-manager/backend/` directory:
```bash
# 1. Activate the python virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# 2. Start the Uvicorn application server
uvicorn main:app --reload --port 8000
```
The backend API will run on [http://localhost:8000](http://localhost:8000).

### Frontend (React + Vite)
From the `bill-manager/frontend/` directory:
```bash
# Run the dev server
npm run dev
```
The frontend UI will run on [http://localhost:5173](http://localhost:5173).

---

## Environment Variables List

The backend uses a local `.env` configuration file to load settings. The following variables are supported:

| Key | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./bill_manager.db` | Connection string to SQLite database file |
| `UPLOAD_DIR` | `../uploads` | Path to save physical bill/invoice files (relative to `backend/`) |
| `SECRET_KEY` | `changeme` | Secret key used for hash encryption signatures |

---

## What Comes Next (Section 2 Preview)

In the next section, we will:
1. **Define Database Schemas**: Set up SQLAlchemy models for transactions, extracted line items, and vendors using SQLite.
2. **Implement OCR Processing Pipeline**: Build a three-tier pipeline (e.g., pdfplumber, pytesseract, and LLM text extraction) to parse bills, receipts, and invoices.
3. **Create API Routes**: Construct endpoints for uploading files (`POST /api/bills/upload`), triggering extraction, and fetching historical transactions.
