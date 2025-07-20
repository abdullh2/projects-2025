 
import cv2
import os
import numpy as np

image_dir = "data/images/train"
label_dir = "data/labels/train"

for img_name in os.listdir(image_dir):
    img_path = os.path.join(image_dir, img_name)
    label_path = os.path.join(label_dir, img_name.replace('.jpg', '.txt'))
    
    image = cv2.imread(img_path)
    h, w = image.shape[:2]
    
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            for line in f:
                class_id, x, y, w, h = map(float, line.split())
                x1 = int((x - w/2) * w)
                y1 = int((y - h/2) * h)
                x2 = int((x + w/2) * w)
                y2 = int((y + h/2) * h)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, f"Class {int(class_id)}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imshow("Image", image)
    cv2.waitKey(0)
cv2.destroyAllWindows()