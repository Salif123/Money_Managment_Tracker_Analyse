from dataclasses import dataclass

@dataclass
class OCRResult:
    text: str
    confidence: float  # Value between 0.0 and 1.0
    engine: str        # Name of the engine used (e.g. "tesseract", "paddle", "vision_llm")

CONFIDENCE_THRESHOLD_T1 = 0.75
CONFIDENCE_THRESHOLD_T2 = 0.70
