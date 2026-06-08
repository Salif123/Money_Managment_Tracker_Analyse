import logging
from .base import OCRResult

logger = logging.getLogger(__name__)

# Lazy initialization of PaddleOCR instance
_paddle_ocr_instance = None

def _get_paddle_ocr():
    global _paddle_ocr_instance
    if _paddle_ocr_instance is None:
        try:
            import os
            # Disable oneDNN to bypass regression crash in PaddlePaddle 3.3.x on Windows CPU inference
            os.environ['FLAGS_use_onednn'] = '0'
            os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
            
            from paddleocr import PaddleOCR
            from paddleocr import logger as paddle_logger
            import logging
            # Suppress paddle logging
            paddle_logger.setLevel(logging.ERROR)
            logging.getLogger("ppocr").setLevel(logging.ERROR)
            _paddle_ocr_instance = PaddleOCR(use_angle_cls=True, lang='en', enable_mkldnn=False)
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise e
    return _paddle_ocr_instance

def run_paddle(image_path: str) -> OCRResult:
    """
    Runs PaddleOCR on the given image.
    Concatenates detected text lines and calculates mean confidence.
    """
    try:
        ocr = _get_paddle_ocr()
        result = ocr.ocr(image_path)
    except Exception as e:
        logger.error(f"PaddleOCR execution failed: {e}")
        # Return empty result with 0 confidence
        return OCRResult(text="", confidence=0.0, engine="paddle")

    text_lines = []
    scores = []

    # Handle PaddleOCR 3.x (returns list of OCRResult objects containing rec_texts and rec_scores)
    # and legacy PaddleOCR (returns list of lines containing [box, (text, confidence)])
    if result and result[0]:
        item = result[0]
        # Check for PaddleOCR 3.x format (object/dict with rec_texts and rec_scores)
        if hasattr(item, "rec_texts") and hasattr(item, "rec_scores"):
            text_lines = item.rec_texts
            scores = [float(s) for s in item.rec_scores]
        elif hasattr(item, "get") or isinstance(item, dict):
            try:
                text_lines = item.get("rec_texts", [])
                scores = [float(s) for s in item.get("rec_scores", [])]
            except Exception as e:
                logger.warning(f"Failed to get rec_texts from dict-like PaddleOCR result: {e}")
        
        # Fallback to legacy format if no text lines extracted
        if not text_lines:
            try:
                for line in item:
                    if line and len(line) >= 2:
                        box_info, text_conf = line
                        if isinstance(text_conf, (list, tuple)) and len(text_conf) >= 2:
                            text, conf = text_conf
                            text_lines.append(str(text))
                            scores.append(float(conf))
            except Exception as e:
                logger.warning(f"Failed to parse legacy PaddleOCR output: {e}")

    full_text = "\n".join(text_lines)
    mean_conf = sum(scores) / len(scores) if scores else 0.0

    return OCRResult(
        text=full_text,
        confidence=mean_conf,
        engine="paddle"
    )
