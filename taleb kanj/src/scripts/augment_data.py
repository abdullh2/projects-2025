 
import albumentations as A
import cv2
import os
import numpy as np


transform = A.Compose([
    A.Rotate(limit=30, p=0.5),
    A.RandomBrightnessContrast(p=0.5),
    A.GaussianBlur(p=0.3),
    A.Flip(p=0.5),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))


image_dir = "data/images/train"
label_dir = "data/labels/train"
output_image_dir = "data/images/augmented"
output_label_dir = "data/labels/augmented"

os.makedirs(output_image_dir, exist_ok=True)
os.makedirs(output_label_dir, exist_ok=True)

for img_name in os.listdir(image_dir):
    img_path = os.path.join(image_dir, img_name)
    label_path = os.path.join(label_dir, img_name.replace('.jpg', '.txt'))
    
  
    image = cv2.imread(img_path)
    bboxes = []
    class_labels = []
    if os.path.exists(label_path):
        with open(label_path, 'r') as f:
            for line in f:
                class_id, x, y, w, h = map(float, line.split())
                bboxes.append([x, y, w, h])
                class_labels.append(int(class_id))
    
   
    augmented = transform(image=image, bboxes=bboxes, class_labels=class_labels)
    aug_image = augmented['image']
    aug_bboxes = augmented['bboxes']
    aug_labels = augmented['class_labels']
    

    aug_img_path = os.path.join(output_image_dir, f"aug_{img_name}")
    cv2.imwrite(aug_img_path, aug_image)
    
  
    aug_label_path = os.path.join(output_label_dir, f"aug_{img_name.replace('.jpg', '.txt')}")
    with open(aug_label_path, 'w') as f:
        for bbox, label in zip(aug_bboxes, aug_labels):
            f.write(f"{label} {' '.join(map(str, bbox))}\n")