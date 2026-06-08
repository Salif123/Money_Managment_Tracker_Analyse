import logging
from .base import OCRResult, CONFIDENCE_THRESHOLD_T1, CONFIDENCE_THRESHOLD_T2
from .tier1_tesseract import run_tesseract
from .tier2_paddle import run_paddle
from .tier3_vision import run_vision_llm, OllamaNotAvailableError

logger = logging.getLogger(__name__)

def extract_text(image_path: str) -> OCRResult:
    """
    Executes the 3-tier OCR engine workflow:
    1. Tries Tier 1 (Tesseract). If confidence >= 0.75, returns immediately.
    2. Tries Tier 2 (PaddleOCR). If confidence >= 0.70, returns immediately.
    3. Tries Tier 3 (Ollama Llava Vision LLM). If Ollama is not available,
       logs a warning and falls back to the best result found between Tier 1 and Tier 2.
    """
    t1_result = None
    t2_result = None

    # Tier 1: Tesseract
    logger.info(f"Running OCR Tier 1 (Tesseract) on {image_path}...")
    try:
        t1_result = run_tesseract(image_path)
        logger.info(f"Tier 1 (Tesseract) confidence: {t1_result.confidence:.4f}")
        if t1_result.confidence >= CONFIDENCE_THRESHOLD_T1:
            logger.info("Tier 1 confidence exceeds threshold. Returning result.")
            return t1_result
    except Exception as e:
        logger.warning(f"Tier 1 (Tesseract) failed to execute: {e}", exc_info=True)

    # Tier 2: PaddleOCR
    logger.info(f"Escalating to OCR Tier 2 (PaddleOCR) on {image_path}...")
    try:
        t2_result = run_paddle(image_path)
        logger.info(f"Tier 2 (PaddleOCR) confidence: {t2_result.confidence:.4f}")
        if t2_result.confidence >= CONFIDENCE_THRESHOLD_T2:
            logger.info("Tier 2 confidence exceeds threshold. Returning result.")
            return t2_result
    except Exception as e:
        logger.warning(f"Tier 2 (PaddleOCR) failed to execute: {e}", exc_info=True)

    # Tier 3: Vision LLM via Ollama
    logger.info(f"Escalating to OCR Tier 3 (Vision LLM) on {image_path}...")
    try:
        t3_result = run_vision_llm(image_path)
        logger.info("Tier 3 (Vision LLM) executed successfully. Returning result.")
        return t3_result
    except OllamaNotAvailableError as e:
        logger.warning(f"Tier 3 (Vision LLM) not available: {e}. Falling back to best Tier 1/2 result.")
    except Exception as e:
        logger.warning(f"Tier 3 (Vision LLM) failed: {e}. Falling back to best Tier 1/2 result.", exc_info=True)

    # Fallback: Determine the best result found so far
    candidates = [cand for cand in (t1_result, t2_result) if cand is not None]
    if candidates:
        best_candidate = max(candidates, key=lambda c: c.confidence)
        logger.info(f"Using fallback engine '{best_candidate.engine}' with confidence {best_candidate.confidence:.4f}")
        return best_candidate

    logger.error("All OCR tiers failed. Returning empty result.")
    return OCRResult(text="", confidence=0.0, engine="failed")
