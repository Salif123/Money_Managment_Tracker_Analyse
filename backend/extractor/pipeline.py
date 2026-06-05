import os
import cv2
import uuid
import pdfplumber
from dataclasses import dataclass
from typing import List, Optional

from config import upload_path
from .detector import detect_file_type, FileType
from .preprocessor import pdf_to_images, preprocess_image, save_preprocessed

@dataclass
class PreparedFile:
    file_type: FileType
    image_paths: List[str]      # Absolute or relative paths to preprocessed PNG images
    raw_pdf_text: Optional[str] = None  # Full extracted text for digital PDFs only

def prepare_file(file_path: str) -> PreparedFile:
    """
    Orchestrates the first stage of the extraction pipeline:
    1. Detects file type.
    2. If DIGITAL_PDF, extracts all text.
    3. If SCANNED_PDF, converts pages to images, preprocesses each page, and saves them.
    4. If IMAGE, reads the image, preprocesses it, and saves it.
    """
    # Detect file type
    file_type = detect_file_type(file_path)
    
    # Ensure preprocessed output directory exists
    preprocessed_dir = os.path.join(upload_path, "preprocessed")
    os.makedirs(preprocessed_dir, exist_ok=True)
    
    # Extract file_id from filename if it matches our pattern "{uuid}_{original_filename}"
    basename = os.path.basename(file_path)
    if "_" in basename:
        file_id = basename.split("_")[0]
    else:
        file_id = str(uuid.uuid4())
        
    image_paths = []
    raw_pdf_text = None

    if file_type == FileType.DIGITAL_PDF:
        # Extract text from all pages
        text_pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_pages.append(text)
            raw_pdf_text = "\n".join(text_pages)
        except Exception as e:
            # Fallback if parsing fails
            raw_pdf_text = ""
            
    elif file_type == FileType.SCANNED_PDF:
        # Convert pages to images
        pages = pdf_to_images(file_path)
        for idx, page_img in enumerate(pages):
            preprocessed_img = preprocess_image(page_img)
            # Define output path
            out_filename = f"{file_id}_page_{idx + 1}.png"
            out_path = os.path.join(preprocessed_dir, out_filename)
            save_preprocessed(preprocessed_img, out_path)
            # Store relative or absolute path. Let's store absolute path, or relative path to upload_path
            # Let's store relative path or standard path to keep it consistent
            # The prompt says: "save PNGs to uploads/preprocessed/". Let's save and store relative path: "uploads/preprocessed/{filename}"
            # Let's make it relative to the upload_path or project root depending on how FastAPI serves it.
            # Since the router returns a preview_url which maps to /uploads/preprocessed/..., storing the relative path from the upload_path is ideal.
            # Let's store the relative path from project root: "uploads/preprocessed/{filename}"
            rel_path = f"uploads/preprocessed/{out_filename}"
            image_paths.append(rel_path)
            
    elif file_type == FileType.IMAGE:
        # Load image
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError(f"Could not read image file at {file_path}")
            
        preprocessed_img = preprocess_image(img)
        out_filename = f"{file_id}_preprocessed.png"
        out_path = os.path.join(preprocessed_dir, out_filename)
        save_preprocessed(preprocessed_img, out_path)
        
        rel_path = f"uploads/preprocessed/{out_filename}"
        image_paths.append(rel_path)
        
    return PreparedFile(
        file_type=file_type,
        image_paths=image_paths,
        raw_pdf_text=raw_pdf_text
    )
