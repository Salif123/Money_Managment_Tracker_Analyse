import cv2
import numpy as np
import pdf2image
from PIL import Image

def pdf_to_images(file_path: str, dpi: int = 300) -> list[np.ndarray]:
    """
    Converts a PDF file into a list of OpenCV-compatible BGR images.
    """
    # convert_from_path returns a list of PIL Images
    pil_images = pdf2image.convert_from_path(file_path, dpi=dpi)
    cv_images = []
    for pil_img in pil_images:
        # Convert PIL image to BGR numpy array
        rgb_img = np.array(pil_img)
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
        cv_images.append(bgr_img)
    return cv_images

def _deskew(gray: np.ndarray) -> np.ndarray:
    """
    Finds the rotation skew angle of the text lines and rotates the image back.
    Uses Hough line detection to compute median slant and warps the image.
    """
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    # Detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    
    angle = 0.0
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Calculate rotation angle in degrees
            theta = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            # Focus on small angle deviations (mostly horizontal lines in documents)
            if -45 < theta < 45:
                angles.append(theta)
        
        if angles:
            angle = np.median(angles)
            
    # Apply deskew if there is a detectable rotation slant
    if abs(angle) > 0.1:
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        # Calculate rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        # Warp affine to rotate. Fill new empty space with white border (255)
        gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=255)
        
    return gray

def preprocess_image(img: np.ndarray) -> np.ndarray:
    """
    Applies the full preprocessing pipeline:
      1. Grayscale
      2. Deskew
      3. Denoise
      4. Binarize
      5. Upscale (if width < 1500px)
      6. Border cleanup (crop 10px)
    Returns:
      Cleaned single-channel grayscale image (uint8).
    """
    # 1. Grayscale
    if len(img.shape) == 3:
        if img.shape[2] == 4:
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        else:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # 2. Deskew
    deskewed = _deskew(gray)

    # 3. Denoise (h=10 for strength)
    denoised = cv2.fastNlMeansDenoising(deskewed, h=10)

    # 4. Binarize using OTSU thresholding
    _, binarized = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 5. Upscale if width < 1500px
    h, w = binarized.shape[:2]
    if w < 1500:
        scale = 1500.0 / w
        new_w = 1500
        new_h = int(h * scale)
        upscaled = cv2.resize(binarized, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    else:
        upscaled = binarized

    # 6. Border cleanup - Crop 10px from all edges
    h_up, w_up = upscaled.shape[:2]
    if h_up > 20 and w_up > 20:
        cropped = upscaled[10:h_up-10, 10:w_up-10]
    else:
        cropped = upscaled

    return cropped

def save_preprocessed(img: np.ndarray, output_path: str) -> str:
    """
    Saves the preprocessed image to output_path as a PNG and returns the path.
    """
    cv2.imwrite(output_path, img)
    return output_path
