from ultralytics import YOLO
import cv2

model = YOLO("./runs/detect/aerial_detection_v18/weights/best.pt")

results = model.predict(source="./test_images", save=True)

for result in results:
    img = result.plot()  
    cv2.imshow("Prediction", img)
    if cv2.waitKey(0) & 0xFF == ord('q'): 
        break
cv2.destroyAllWindows()