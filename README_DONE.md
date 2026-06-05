# Bill Manager - Local Invoice/Bill Management App

Welcome to **Bill Manager**, a local invoice and bill management application designed to classify, preprocess, extract, and catalog billing transactions. This documentation covers the complete setup for:
- **Section 1 (App Scaffolding)**
- **Section 2 (Database Models, Migrations, & API Endpoints)**
- **Section 3 (File Detection & Image Preprocessing Pipeline)**

---

## What is Built

### 1. File Detection & Preprocessing (Section 3)
- **File Type Detector (`backend/extractor/detector.py`)**:
  - Leverages `python-magic` to inspect file headers and determine MIME types.
  - Leverages `pdfplumber` to check if a PDF is digital or scanned: extracts text from the first page and marks it as `DIGITAL_PDF` if $> 50$ characters of text exist; otherwise, classifies it as `SCANNED_PDF`.
  - Classifies any `image/*` file format as `IMAGE`.
- **OpenCV Image Preprocessor (`backend/extractor/preprocessor.py`)**:
  - Handles PDF-to-image conversions via `pdf2image`.
  - Cleans up and standardizes scanned documents/images:
    1. **Grayscale**: Converts BGR/BGRA images to single-channel gray.
    2. **Deskew**: Uses Hough Line Transform (`cv2.HoughLinesP`) to compute text alignment angles and rotates the document using `cv2.warpAffine` with a solid white background filling.
    3. **Denoise**: Minimizes camera noise and grain using `cv2.fastNlMeansDenoising` ($h=10$).
    4. **Binarize**: Applies Otsu's thresholding (`cv2.THRESH_BINARY + cv2.THRESH_OTSU`) for crisp black-and-white contrast.
    5. **Upscale**: Automatically scales up any images with width $< 1500$ px using cubic interpolation (`cv2.INTER_CUBIC`) to improve OCR precision.
    6. **Crop**: Crops a 10px margin off all edges to clean up scanner borders.
- **Pipeline Orchestrator (`backend/extractor/pipeline.py`)**:
  - Connectes detector and preprocessor modules.
  - Automatically isolates UUID prefixes from saved files to output page PNGs as `uploads/preprocessed/{uuid}_page_{idx}.png` (scanned PDFs) or `uploads/preprocessed/{uuid}_preprocessed.png` (images).
  - Returns a structured `PreparedFile` dataclass.
- **Upload API Router (`backend/routers/upload.py`)**:
  - Mounts `POST /api/upload/prepare` accepting multipart file uploads (PDF, JPG, PNG, WEBP, TIFF).
  - Enforces a size limit of $20$ MB.
  - Validates actual file MIME types.
  - Returns file metadata, page counts, and the static preview URL of the preprocessed image.

### 2. Python 3.11 Backend (FastAPI Core)
- **Settings & Config**: Configured with `pydantic-settings` to load environments (`.env`).
- **Database Engine (`backend/database.py`)**: SQLite integration configured with thread-safety hooks.
- **SQLAlchemy Schemas (`backend/models.py`)**:
  - `Vendor`: Profile info (name, address, email, phone, GSTIN, PAN).
  - `Invoice`: Header totals, file paths, extraction method, notes, and soft-delete support (`deleted_at`).
  - `LineItem`: Descriptions, quantity, unit, price, and breakdown taxes (CGST, SGST, IGST).
  - `TaxEntry`: Summary calculations grouped by rate percentages.
  - `Category` & `InvoiceCategory`: Categorization tagging (name, hex color) using a many-to-many relationship mapping.
- **Alembic Migrations**: Dynamically loads schemas to run migrations on the local database file.
- **API Routers**:
  - `health`: Service check endpoint.
  - `invoices`: GET/PATCH/DELETE endpoints for database catalog items.

### 3. React 18 Frontend (Vite + Tailwind CSS)
- **Vite Proxy Config**: Proxy maps `/api` requests to Uvicorn running on port 8000.
- **Styling**: Tailwind CSS v3 including the `@tailwindcss/forms` plugin.
- **Dashboard Workspace**: Beautiful dark-themed sidebar, active navigation, and live API diagnostic health checks.

---

## Folder Structure

```text
bill-manager/
├── backend/
│   ├── alembic/                 # Alembic migration scripts and environment
│   ├── crud/                    # Database query helper files
│   ├── extractor/               # Section 3: Extraction Pipeline Engine
│   │   ├── detector.py          # Classifies digital/scanned PDFs and images
│   │   ├── pipeline.py          # Orchestrates processing and formats output
│   │   └── preprocessor.py      # OpenCV deskew, denoise, and binarization logic
│   ├── routers/                 # FastAPI routes definitions
│   │   ├── health.py            # Status verification
│   │   ├── invoices.py          # CRUD endpoints
│   │   └── upload.py            # Section 3: File upload and preparation endpoint
│   ├── tests/                   # Extraction validation scripts
│   │   ├── test_preprocessor.py # Downloads sample invoice and runs OpenCV check
│   │   ├── sample_invoice.png   # (Downloaded test asset)
│   │   └── sample_invoice_preproc.png  # (Preprocessed output asset)
│   ├── alembic.ini              # Alembic environment config
│   ├── config.py                # App settings loader
│   ├── database.py              # DB engine & sessionmaker config
│   ├── main.py                  # API endpoints mount & static folder service
│   ├── models.py                # SQLAlchemy database models
│   ├── requirements.txt         # Backend Python dependencies list
│   └── .env                     # Local configuration secrets (gitignored)
├── dataset/                     # Testing data directory
│   └── archive (1).zip          # ~479MB invoice dataset zip for local testing
├── frontend/                    # React frontend application
├── uploads/                     # Storage folder for invoices (gitignored)
│   ├── originals/               # Stores raw files uploaded by users
│   └── preprocessed/            # Stores preprocessed monochrome page PNGs
├── .gitignore                   # Exclude list for git commits
└── README_DONE.md               # Summary of Complete Project Features
```

---

## Installation & System Dependencies

### 1. System Packages
The preprocessing pipeline relies on system packages for document handling and MIME detection:

#### **poppler-utils** (For converting PDF to images)
- **Ubuntu/Debian**:
  ```bash
  sudo apt update && sudo apt install -y poppler-utils
  ```
- **macOS**:
  ```bash
  brew install poppler
  ```
- **Windows**:
  - Install via Scoop: `scoop install poppler`
  - Install via Chocolatey: `choco install poppler`
  - Or download compiled binaries from release pages (e.g. [@oschwartz10612's poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)) and add its `bin/` directory to the system environment variables `PATH`.

#### **libmagic** (For MIME checks)
- **Ubuntu/Debian**:
  ```bash
  sudo apt update && sudo apt install -y libmagic1
  ```
- **macOS**:
  ```bash
  brew install libmagic
  ```
- **Windows**:
  - **No manual install required**. The backend automatically installs `python-magic-bin` when running on Windows, which bundles precompiled `libmagic` DLL files.

---

## How to Run

### 1. Run Migrations & Start Backend
From the `backend/` directory:

```powershell
# 1. Activate the virtual environment:
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# 2. Run database migrations:
alembic upgrade head

# 3. Start FastAPI server:
uvicorn main:app --reload --port 8000
```
*The API server will spin up on [http://localhost:8000](http://localhost:8000).*

### 2. Run Frontend
From the `frontend/` directory in a new terminal window:
```bash
npm install
npm run dev
```
*The UI dashboard will start on [http://localhost:5173](http://localhost:5173).*

---

## Local Testing Dataset
A local dataset containing real-world invoice images and PDFs is available inside the project directory:
- **Location**: `dataset/archive (1).zip` (Size: ~479MB)
- **Usage**: You can unzip this archive to extract diverse invoice styles (multipage, skewed, low resolution) to test and benchmark the preprocessing and file type detection endpoints.

---

## API Verification Cheatsheet

### 1. Upload & Preprocess File (POST)
Send a PDF or image file to the backend:
```bash
curl.exe -X POST -F "file=@tests/sample_invoice.png" http://localhost:8000/api/upload/prepare
```

**Response Format**:
```json
{
  "file_id": "cfde58b8-bf43-437f-b459-12f7c1ad3346",
  "file_type": "IMAGE",
  "pages": 1,
  "preview_url": "/uploads/preprocessed/cfde58b8-bf43-437f-b459-12f7c1ad3346_preprocessed.png"
}
```

### 2. Standalone Preprocessing Script
You can test the OpenCV preprocessing suite offline using the built-in test script. From the `backend/` directory:
```bash
python tests/test_preprocessor.py
```
This script downloads a template invoice, runs grayscaling, deskewing, denoising, binarization, resizing, and border cropping, and logs the dimension metrics before and after the transforms.

### 3. Database Invoices (GET/PATCH/DELETE)
- **List Invoices**: `curl http://localhost:8000/api/invoices`
- **Get Invoice Details**: `curl http://localhost:8000/api/invoices/{uuid}`
- **Update Invoice Notes**: `curl -X PATCH -H "Content-Type: application/json" -d '{"notes": "Updated text"}' http://localhost:8000/api/invoices/{uuid}/notes`
- **Soft-Delete**: `curl -X DELETE http://localhost:8000/api/invoices/{uuid}`
