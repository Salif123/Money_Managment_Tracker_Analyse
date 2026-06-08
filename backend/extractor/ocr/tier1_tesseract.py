import pytesseract
from PIL import Image
from .base import OCRResult

def run_tesseract(image_path: str) -> OCRResult:
    """
    Runs Tesseract OCR on the given image.
    Calculates confidence as the mean of all non-negative word confidence values.
    Returns OCRResult.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Could not open image file {image_path}: {e}")

    # Try eng+hin first, then fallback to eng if there is an error
    # (e.g., if the user doesn't have the Hindi language pack installed)
    try:
        data = pytesseract.image_to_data(img, lang="eng+hin", output_type=pytesseract.Output.DICT)
        full_text = pytesseract.image_to_string(img, lang="eng+hin").strip()
    except Exception:
        data = pytesseract.image_to_data(img, lang="eng", output_type=pytesseract.Output.DICT)
        full_text = pytesseract.image_to_string(img, lang="eng").strip()

    # Extract confidence values (pytesseract confidence ranges from 0 to 100, or -1 for metadata blocks)
    conf_values = [
        float(conf) 
        for conf in data.get("conf", []) 
        if conf is not None and float(conf) >= 0
    ]
    
    mean_conf = (sum(conf_values) / len(conf_values)) if conf_values else 0.0
    
    return OCRResult(
        text=full_text,
        confidence=mean_conf / 100.0,
        engine="tesseract"
    )
