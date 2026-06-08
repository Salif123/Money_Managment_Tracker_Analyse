import os
import uuid
import magic
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from pydantic import BaseModel

from config import upload_path
from extractor.pipeline import prepare_file, FileType

router = APIRouter(tags=["upload"])

# Define validation limits
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/tiff"
}

class UploadPrepareResponse(BaseModel):
    file_id: str
    file_type: FileType
    pages: int
    preview_url: Optional[str] = None
    ocr_engine_used: str
    ocr_confidence: float
    raw_text_preview: str

@router.post("/upload/prepare", response_model=UploadPrepareResponse)
async def upload_prepare(file: UploadFile = File(...)):
    """
    Accepts an upload of an invoice file, validates it, saves the original,
    and runs the preprocessing pipeline.
    """
    # 1. Read file to validate size
    contents = await file.read()
    file_size = len(contents)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / (1024 * 1024):.2f}MB) exceeds the 20MB limit."
        )

    # Ensure originals directory exists
    originals_dir = os.path.join(upload_path, "originals")
    os.makedirs(originals_dir, exist_ok=True)

    # 2. Save original file using a unique name to avoid conflicts
    file_id = str(uuid.uuid4())
    safe_filename = os.path.basename(file.filename)
    dest_filename = f"{file_id}_{safe_filename}"
    dest_path = os.path.join(originals_dir, dest_filename)

    try:
        with open(dest_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # 3. Validate MIME type using python-magic on the saved file
    try:
        mime = magic.from_file(dest_path, mime=True)
    except Exception as e:
        # Fallback to file content type if magic check fails
        mime = file.content_type

    if mime not in ALLOWED_MIME_TYPES:
        # Delete file if validation fails
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{mime}'. Allowed types: PDF, JPEG, PNG, WEBP, TIFF."
        )

    # 4. Process file through the extraction/preprocessing pipeline
    try:
        prepared = prepare_file(dest_path)
    except Exception as e:
        # Clean up original file on processing error
        if os.path.exists(dest_path):
            os.remove(dest_path)
        raise HTTPException(
            status_code=500,
            detail=f"File preprocessing failed: {str(e)}"
        )

    # Calculate page count and preview URL
    # For digital PDF, pages can be read from pdfplumber
    # For scanned PDF, page count equals count of image paths
    # For image, page count is 1
    if prepared.file_type == FileType.DIGITAL_PDF:
        import pdfplumber
        try:
            with pdfplumber.open(dest_path) as pdf:
                pages_count = len(pdf.pages)
        except Exception:
            pages_count = 1
        preview_url = None
    elif prepared.file_type == FileType.SCANNED_PDF:
        pages_count = len(prepared.image_paths)
        preview_url = f"/{prepared.image_paths[0]}" if prepared.image_paths else None
    else:  # FileType.IMAGE
        pages_count = 1
        preview_url = f"/{prepared.image_paths[0]}" if prepared.image_paths else None

    return UploadPrepareResponse(
        file_id=file_id,
        file_type=prepared.file_type,
        pages=pages_count,
        preview_url=preview_url,
        ocr_engine_used=prepared.ocr_engine_used,
        ocr_confidence=prepared.ocr_confidence,
        raw_text_preview=prepared.raw_text[:300]
    )
