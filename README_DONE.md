# Bill Manager - Local Invoice/Bill Management App

Welcome to **Bill Manager**, a local invoice and bill management application designed to classify, preprocess, extract, and catalog billing transactions. This documentation covers the complete setup for:
- **Section 1 (App Scaffolding)**
- **Section 2 (Database Models, Migrations, & API Endpoints)**
- **Section 3 (File Detection & Image Preprocessing Pipeline)**
- **Section 4 (3-tier OCR Extraction Engine)**

---

## What is Built

### 1. 3-tier OCR Engine (Section 4)
- **Multi-tiered Orchestration (`backend/extractor/ocr/engine.py`)**:
  - Automatically processes preprocessed page images sequentially.
  - Tries Tier 1 first. If confidence is below the threshold, it escalates to Tier 2. If Tier 2 confidence is also below the threshold, it escalates to Tier 3 (Ollama Vision LLM).
- **Tier 1 - Tesseract OCR (`backend/extractor/ocr/tier1_tesseract.py`)**:
  - Uses `pytesseract` to call local Tesseract binary.
  - Queries `image_to_data` using `lang="eng+hin"` (falling back to `"eng"` if Hindi training data is missing).
  - Computes confidence as the mean of all non-negative word confidence values.
  - Uses a threshold of `CONFIDENCE_THRESHOLD_T1 = 0.75`.
- **Tier 2 - PaddleOCR (`backend/extractor/ocr/tier2_paddle.py`)**:
  - Uses `paddleocr` with `use_angle_cls=True` (and disables oneDNN and MKLDNN dynamically to prevent Windows CPU execution crashes).
  - Lazily initializes the PaddleOCR instance globally to prevent startup and page-to-page model reloading overhead.
  - Parses text lines and computes confidence as the mean score across lines.
  - Uses a threshold of `CONFIDENCE_THRESHOLD_T2 = 0.70`.
- **Tier 3 - Vision LLM via Ollama (`backend/extractor/ocr/tier3_vision.py`)**:
  - Encodes preprocessed page images in Base64.
  - Posts requests to a local Ollama instance running the `llava` multi-modal vision model.
  - Catches connectivity errors (`OllamaNotAvailableError`) and falls back to the highest confidence result found in Tier 1 or Tier 2.
- **Enhanced Preparation Pipeline (`backend/extractor/pipeline.py`)**:
  - Updates `prepare_file()` to run OCR on each page image.
  - Concatenates page texts and calculates average confidence and unique engines used across pages.
- **Updated Upload Endpoint (`backend/routers/upload.py`)**:
  - `POST /api/upload/prepare` returns details:
    `{ ..., ocr_engine_used: str, ocr_confidence: float, raw_text_preview: str }`

### 2. File Detection & Preprocessing (Section 3)
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

### 3. Python 3.11 Backend (FastAPI Core)
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
  - `upload`: File preprocessing and metadata extraction endpoint.

### 4. React 18 Frontend (Vite + Tailwind CSS)
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
│   ├── extractor/               # Extraction Pipeline Engine
│   │   ├── ocr/                 # Section 4: 3-tier OCR Engine
│   │   │   ├── base.py          # OCR dataclasses and threshold settings
│   │   │   ├── engine.py        # Orchestration and T1 -> T2 -> T3 escalation logic
│   │   │   ├── tier1_tesseract.py  # Tier 1 Tesseract wrapper
│   │   │   ├── tier2_paddle.py     # Tier 2 PaddleOCR wrapper
│   │   │   └── tier3_vision.py     # Tier 3 Ollama Vision LLM wrapper
│   │   ├── detector.py          # Classifies digital/scanned PDFs and images
│   │   ├── pipeline.py          # Orchestrates processing and formats output
│   │   └── preprocessor.py      # OpenCV deskew, denoise, and binarization logic
│   ├── routers/                 # FastAPI routes definitions
│   │   ├── health.py            # Status verification
│   │   ├── invoices.py          # CRUD endpoints
│   │   └── upload.py            # File upload, preprocessing, and OCR endpoint
│   ├── tests/                   # Extraction validation scripts
│   │   ├── test_preprocessor.py # Downloads sample invoice and runs OpenCV check
│   │   ├── test_ocr.py          # Verifies OCR engine tiers and orchestration
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
│   └── ...
├── uploads/                     # Storage folder for invoices (gitignored)
│   ├── originals/               # Stores raw files uploaded by users
│   └── preprocessed/            # Stores preprocessed monochrome page PNGs
├── .gitignore                   # Exclude list for git commits
└── README_DONE.md               # Summary of Complete Project Features
```

---

## Installation & System Dependencies

### 1. OCR Engine Binaries
The OCR engine relies on local binaries:

#### **Tesseract OCR (Tier 1)**
- **Ubuntu/Debian**:
  ```bash
  sudo apt update && sudo apt install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin
  ```
- **macOS**:
  ```bash
  brew install tesseract
  ```
- **Windows**:
  - Download and run the installer (e.g. from UB Mannheim's Tesseract wiki: [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)).
  - Add the installation directory (usually `C:\Program Files\Tesseract-OCR`) to your system environment variables `PATH`.

#### **Ollama & Llava Model (Tier 3)**
- Download and install Ollama from [https://ollama.com](https://ollama.com).
- In a terminal, pull the vision model:
  ```bash
  ollama pull llava
  ```
- Keep the Ollama application running on port `11434`.

### 2. File Utilities
#### **poppler-utils** (For converting PDF to images)
- **Ubuntu/Debian**: `sudo apt install -y poppler-utils`
- **macOS**: `brew install poppler`
- **Windows**: Install via Scoop (`scoop install poppler`), Chocolatey (`choco install poppler`), or download binaries and append to `PATH`.

#### **libmagic** (For MIME checks)
- **Ubuntu/Debian**: `sudo apt install -y libmagic1`
- **macOS**: `brew install libmagic`
- **Windows**: Installed automatically as a bundled DLL via `python-magic-bin` package.

---

## How to Run

### 1. Run Migrations & Start Backend
From the `backend/` directory:

```powershell
# 1. Activate virtual environment:
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# 2. Run database migrations:
alembic upgrade head

# 3. Start FastAPI server:
uvicorn main:app --reload --port 8000
```

### 2. Run Frontend
From the `frontend/` directory in a new terminal:
```bash
npm install
npm run dev
```

---

## API Verification Cheatsheet

### 1. Upload & Extract Text (POST)
Send a PDF or image file to the backend:
```bash
curl.exe -X POST -F "file=@tests/sample_invoice.png" http://localhost:8000/api/upload/prepare
```

**Response Format**:
```json
{
  "file_id": "4cbbc84c-c923-4d1f-b484-2c9a71031a08",
  "file_type": "IMAGE",
  "pages": 1,
  "preview_url": "/uploads/preprocessed/4cbbc84c-c923-4d1f-b484-2c9a71031a08_preprocessed.png",
  "ocr_engine_used": "tesseract",
  "ocr_confidence": 0.87617,
  "raw_text_preview": "INVOICE\n\nEast Repale Inc.\n\n1912 Harvest Lane..."
}
```

### 2. Standalone OCR Test Script
You can test the OCR tiers and escalation workflow offline. From the `backend/` directory:
```bash
python tests/test_ocr.py
```

---

## Troubleshooting OCR

### 1. Tesseract Language Data Missing
- **Problem**: Tesseract raises an exception like `pytesseract.TesseractError: (1, 'Error opening data file ...')` when trying to use `lang="eng+hin"`.
- **Solution**: The engine is configured to catch this and automatically fall back to `"eng"`. Alternatively, install the Hindi language training data (on Ubuntu: `sudo apt install tesseract-ocr-hin`; on Windows: run the installer and check the language pack options).

### 2. PaddleOCR CPU Execution Crash on Windows (oneDNN / PIR conflict)
- **Problem**: When running PaddleOCR on Windows CPU, a framework crash occurs:
  `PaddleOCR execution failed: (Unimplemented) ConvertPirAttribute2RuntimeAttribute not support [pir::ArrayAttribute<pir::DoubleAttribute>]`
- **Solution**: Set the environment variable `FLAGS_use_onednn=0` before initializing PaddleOCR. This is already handled dynamically in `backend/extractor/ocr/tier2_paddle.py` by configuring `os.environ['FLAGS_use_onednn'] = '0'` and initializing the instance with `enable_mkldnn=False`.

### 3. Ollama Connection Errors (Tier 3)
- **Problem**: When escalating to Tier 3, a warning is logged:
  `Ollama service is not running on http://localhost:11434...`
- **Solution**: Ensure the Ollama app is active in your taskbar/menu and that you have pulled the model (`ollama pull llava`). If Ollama is unavailable, the orchestrator automatically handles it gracefully, logging a warning and falling back to the highest confidence output from Tier 1 or Tier 2.
