import base64
import requests
from .base import OCRResult

class OllamaNotAvailableError(Exception):
    """Exception raised when the Ollama API is not running or llava model is missing."""
    pass

def run_vision_llm(image_path: str) -> OCRResult:
    """
    Encodes the image to base64 and calls Ollama API to extract text using the 'llava' model.
    If Ollama is not running or returns an error, raises OllamaNotAvailableError.
    """
    try:
        with open(image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
    except Exception as e:
        raise ValueError(f"Could not read or encode image file {image_path}: {e}")

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llava",
        "prompt": "Extract all text from this bill or invoice exactly as it appears. Return only the raw text, nothing else.",
        "images": [encoded_image],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        raise OllamaNotAvailableError(
            "Ollama service is not running on http://localhost:11434. "
            "Please ensure Ollama is installed and running, and run 'ollama pull llava' to pull the required model."
        ) from e

    if response.status_code != 200:
        raise OllamaNotAvailableError(
            f"Ollama API returned an error status code {response.status_code}: {response.text}. "
            "Please make sure the 'llava' model has been downloaded by running 'ollama pull llava'."
        )

    try:
        data = response.json()
        extracted_text = data.get("response", "").strip()
    except Exception as e:
        raise OllamaNotAvailableError(f"Failed to parse Ollama API JSON response: {e}") from e

    return OCRResult(
        text=extracted_text,
        confidence=0.95,
        engine="vision_llm"
    )
