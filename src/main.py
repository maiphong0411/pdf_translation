import cv2
import easyocr
import numpy as np

def extract_highest_confidence_text_info(image_path, languages=['en']):
    # Load image
    img = cv2.imread(image_path)

    # Initialize EasyOCR
    reader = easyocr.Reader(languages, gpu=False)
    results = reader.readtext(image_path)

    if not results:
        return None  # No text found

    best_result = max(results, key=lambda r: r[2])  # r[2] is confidence
    bbox, text, confidence = best_result
    (tl, tr, br, bl) = bbox

    # Estimate font size
    height1 = np.linalg.norm(np.array(tl) - np.array(bl))
    height2 = np.linalg.norm(np.array(tr) - np.array(br))
    font_size = (height1 + height2) / 2

    # Get color at center
    center_x = int((tl[0] + br[0]) / 2)
    center_y = int((tl[1] + br[1]) / 2)
    color_bgr = img[center_y, center_x]
    color_rgb = tuple(int(c) for c in color_bgr[::-1])  # BGR → RGB

    return {
        "text": text,
        "confidence": round(confidence, 3),
        "font_size": round(font_size, 2),
        "color_rgb": color_rgb,
        "bbox": bbox
    }

if __name__ == "__main__":
    image_path = "/home/phongmt1/phongmt1/project/pdf_translation/plain text/im.jpg.jpg"  # Replace with your image path
    results = extract_highest_confidence_text_info(image_path)

    print(results)