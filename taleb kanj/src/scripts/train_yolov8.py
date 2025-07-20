from ultralytics import YOLO

model = YOLO("yolov8n.pt")  
results = model.train(
    data="C:\\Aerial_Analysis_Project\\data\\data.yaml",
    epochs=50,
    imgsz=500,
    batch=8,
    name="aerial_detection_v18",
    device="cuda:0",
)
model.save("C:\\Aerial_Analysis_Project\\models\\aerial_detection_v18.pt")