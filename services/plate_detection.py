import cv2
from ultralytics import YOLO

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")  # you can replace with custom model later
    return _model


def detect_plate(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError("Image not found")

    model = _get_model()
    results = model(image, verbose=False)

    for result in results:
        boxes = result.boxes.xyxy
        if len(boxes) > 0:
            scores = result.boxes.conf
            best_idx = int(scores.argmax())

            x1, y1, x2, y2 = map(int, boxes[best_idx])

            plate_crop = image[y1:y2, x1:x2]

            if plate_crop.size > 0:
                return plate_crop

    # fallback
    return image