import os
import sys
import urllib.request
import cv2

# Add the parent directory (backend) to the Python path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extractor.preprocessor import preprocess_image, save_preprocessed

def test():
    # URL of a sample invoice image
    url = "https://templates.invoicehome.com/invoice-template-us-neat-750px.png"
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(test_dir, exist_ok=True)
    input_path = os.path.join(test_dir, "sample_invoice.png")
    output_path = os.path.join(test_dir, "sample_invoice_preprocessed.png")
    
    print(f"Downloading sample invoice from {url}...")
    try:
        # User-agent header to avoid potential HTTP 403 Forbidden issues
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, input_path)
        print(f"Downloaded successfully to {input_path}")
    except Exception as e:
        print(f"Failed to download image: {e}")
        return
        
    # Read the image
    img = cv2.imread(input_path)
    if img is None:
        print(f"Failed to read downloaded image at {input_path}")
        return
        
    h_before, w_before = img.shape[:2]
    channels_before = img.shape[2] if len(img.shape) == 3 else 1
    print(f"Original image info:")
    print(f"  Dimensions: {w_before}x{h_before} (Width x Height)")
    print(f"  Channels: {channels_before}")
    
    # Run preprocessing
    print("Running preprocessing pipeline...")
    try:
        processed_img = preprocess_image(img)
    except Exception as e:
        print(f"Preprocessing failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    h_after, w_after = processed_img.shape[:2]
    channels_after = processed_img.shape[2] if len(processed_img.shape) == 3 else 1
    print(f"Preprocessed image info:")
    print(f"  Dimensions: {w_after}x{h_after} (Width x Height)")
    print(f"  Channels: {channels_after}")
    
    # Save the output
    save_preprocessed(processed_img, output_path)
    print(f"Saved preprocessed image to {output_path}")

if __name__ == "__main__":
    test()
