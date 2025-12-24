import cv2
import pytesseract

def ocr_image(path: str) -> str:
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)[1]
    return pytesseract.image_to_string(img)

