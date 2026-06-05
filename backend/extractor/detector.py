import magic
import pdfplumber
from enum import Enum

class FileType(str, Enum):
    DIGITAL_PDF = "DIGITAL_PDF"
    SCANNED_PDF = "SCANNED_PDF"
    IMAGE = "IMAGE"

def detect_file_type(file_path: str) -> FileType:
    """
    Detects the file type using python-magic and pdfplumber.
    Returns:
        FileType.DIGITAL_PDF: PDF with extractable text (> 50 chars on page 1)
        FileType.SCANNED_PDF: PDF without extractable text (likely scanned images)
        FileType.IMAGE: Standard image files (JPEG, PNG, WEBP, TIFF, etc.)
    """
    # 1. Use python-magic to get mime type
    mime = magic.from_file(file_path, mime=True)

    # 2. If mime is application/pdf
    if mime == "application/pdf":
        try:
            with pdfplumber.open(file_path) as pdf:
                if not pdf.pages:
                    return FileType.SCANNED_PDF
                
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                if text and len(text.strip()) > 50:
                    return FileType.DIGITAL_PDF
                else:
                    return FileType.SCANNED_PDF
        except Exception as e:
            # Fallback if pdfplumber fails to read (could be a corrupted or empty PDF)
            return FileType.SCANNED_PDF

    # 3. If mime is image/*
    if mime and mime.startswith("image/"):
        return FileType.IMAGE

    # Raise error for unsupported file type
    raise ValueError(f"Unsupported file type: {mime}")
