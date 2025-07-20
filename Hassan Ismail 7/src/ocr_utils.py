import easyocr
import cv2

class GPUAcceleratedOCR:
    def __init__(self, lang='en'):
        self.reader = easyocr.Reader([lang], gpu=False)

    def image_to_text(self, image_path):
        image = cv2.imread(image_path)
        results = self.reader.readtext(image)
        text = " ".join([res[1] for res in results])
        confidence = round(sum([res[2] for res in results]) / len(results), 2) if results else 0
        return text, confidence
