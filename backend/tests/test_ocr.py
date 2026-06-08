import os
import sys

# Add the parent directory (backend) to the Python path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extractor.ocr.tier1_tesseract import run_tesseract
from extractor.ocr.tier2_paddle import run_paddle
from extractor.ocr.tier3_vision import run_vision_llm, OllamaNotAvailableError
from extractor.ocr.engine import extract_text

def test_ocr():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(test_dir, "sample_invoice.png")

    if not os.path.exists(image_path):
        print(f"Error: Sample image not found at {image_path}. Run test_preprocessor.py first to download it.")
        sys.exit(1)

    print(f"Using image for OCR tests: {image_path}\n")

    # 1. Test Tier 1 Tesseract
    print("--- Testing Tier 1: Tesseract ---")
    try:
        t1_result = run_tesseract(image_path)
        print(f"Engine: {t1_result.engine}")
        print(f"Confidence: {t1_result.confidence:.4f}")
        print(f"Text Preview (first 150 chars):\n{t1_result.text[:150]}\n")
    except Exception as e:
        print(f"Tier 1 Tesseract failed: {e}\n")

    # 2. Test Tier 2 PaddleOCR
    print("--- Testing Tier 2: PaddleOCR ---")
    try:
        t2_result = run_paddle(image_path)
        print(f"Engine: {t2_result.engine}")
        print(f"Confidence: {t2_result.confidence:.4f}")
        print(f"Text Preview (first 150 chars):\n{t2_result.text[:150]}\n")
    except Exception as e:
        print(f"Tier 2 PaddleOCR failed: {e}\n")

    # 3. Test Tier 3 Vision LLM (Ollama)
    print("--- Testing Tier 3: Ollama Vision LLM ---")
    try:
        t3_result = run_vision_llm(image_path)
        print(f"Engine: {t3_result.engine}")
        print(f"Confidence: {t3_result.confidence:.4f}")
        print(f"Text Preview (first 150 chars):\n{t3_result.text[:150]}\n")
    except OllamaNotAvailableError as e:
        print(f"Tier 3 unavailable: {e}\n")
    except Exception as e:
        print(f"Tier 3 Vision LLM failed: {e}\n")

    # 4. Test Orchestrated Engine (extract_text)
    print("--- Testing Engine Orchestration (extract_text) ---")
    try:
        result = extract_text(image_path)
        print(f"Selected Engine: {result.engine}")
        print(f"Result Confidence: {result.confidence:.4f}")
        print(f"Final Text Preview (first 150 chars):\n{result.text[:150]}\n")
    except Exception as e:
        print(f"Orchestration failed: {e}\n")

if __name__ == "__main__":
    test_ocr()
