import os
import cv2
import uuid
import pdfplumber
from dataclasses import dataclass
from typing import List, Optional

from config import upload_path
from .detector import detect_file_type, FileType
from .preprocessor import pdf_to_images, preprocess_image, save_preprocessed
from .ocr.engine import extract_text

@dataclass
class PreparedFile:
    file_type: FileType
    image_paths: List[str]      # Absolute or relative paths to preprocessed PNG images
    raw_text: str               # Extracted text (digital or OCR)
    ocr_engine_used: str        # Engine used (e.g. "digital", "tesseract", "paddle", etc.)
    ocr_confidence: float       # Confidence score (0.0 to 1.0)

def prepare_file(file_path: str) -> PreparedFile:
    """
    Orchestrates the first stage of the extraction pipeline:
    1. Detects file type.
    2. If DIGITAL_PDF, extracts all text.
    3. If SCANNED_PDF, converts pages to images, preprocesses each page, runs OCR, and saves them.
    4. If IMAGE, reads the image, preprocesses it, runs OCR, and saves it.
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
    page_texts = []
    page_engines = []
    page_confidences = []

    if file_type == FileType.DIGITAL_PDF:
        # Extract text from all pages
        text_pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_pages.append(text)
            raw_text = "\n".join(text_pages)
        except Exception as e:
            # Fallback if parsing fails
            raw_text = ""
        
        # Digital PDFs don't use OCR
        ocr_engine_used = "digital"
        ocr_confidence = 1.0
            
    elif file_type == FileType.SCANNED_PDF:
        # Convert pages to images
        pages = pdf_to_images(file_path)
        for idx, page_img in enumerate(pages):
            preprocessed_img = preprocess_image(page_img)
            # Define output path
            out_filename = f"{file_id}_page_{idx + 1}.png"
            out_path = os.path.join(preprocessed_dir, out_filename)
            save_preprocessed(preprocessed_img, out_path)
            
            # Store path relative to project root
            rel_path = f"uploads/preprocessed/{out_filename}"
            image_paths.append(rel_path)
            
            # Run OCR engine on the preprocessed page image
            ocr_res = extract_text(out_path)
            page_texts.append(ocr_res.text)
            page_engines.append(ocr_res.engine)
            page_confidences.append(ocr_res.confidence)
            
        raw_text = "\n".join(page_texts)
        # Combine unique engines used
        unique_engines = sorted(list(set(page_engines)))
        ocr_engine_used = ", ".join(unique_engines) if unique_engines else "none"
        ocr_confidence = sum(page_confidences) / len(page_confidences) if page_confidences else 0.0
            
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
        
        # Run OCR engine on the preprocessed image
        ocr_res = extract_text(out_path)
        page_texts.append(ocr_res.text)
        page_engines.append(ocr_res.engine)
        page_confidences.append(ocr_res.confidence)
        
        raw_text = "\n".join(page_texts)
        ocr_engine_used = page_engines[0] if page_engines else "none"
        ocr_confidence = page_confidences[0] if page_confidences else 0.0
        
    return PreparedFile(
        file_type=file_type,
        image_paths=image_paths,
        raw_text=raw_text,
        ocr_engine_used=ocr_engine_used,
        ocr_confidence=ocr_confidence
    )

