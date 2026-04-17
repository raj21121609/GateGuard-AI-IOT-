# Number Plate Detection Output & Extraction

This document contains all the extracted logic models and code required for the number plate detection pipeline from your `GateGuard-AI-IOT-` backend codebase. You can recreate this logic in your new project by creating these files.

## 1. [plate_detection.py](file:///c:/Users/user/OneDrive/Desktop/gategaurdAI/GateGuard-AI-IOT-/app/services/plate_detection.py) (YOLOv8 Model Logic)

This file handles the object detection logic using `ultralytics` YOLO, isolating the bounding box crop of the license plate from an image.

```python
"""
Plate Detection using YOLOv8.

On first run the model weights (yolov8n.pt, ~6 MB) are downloaded automatically.
For higher accuracy on number plates, replace with a plate-specific YOLO model.
"""
import cv2
import numpy as np
from ultralytics import YOLO

# Singleton model – loaded once at import time
_model = None


def _get_model() -> YOLO:
    global _model
    if _model is None:
        _model = YOLO("yolov8n.pt")
    return _model


def detect_plate(image_path: str) -> np.ndarray | None:
    """
    Run YOLO on the given image and return the plate bounding-box crop.

    Strategy:
    - If YOLO returns any bounding boxes, take the first one as the plate.
    - If no boxes are found (e.g. generic yolov8n that wasn't trained on plates),
      fall back to returning the full image so OCR can still attempt a read.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Could not read image at: {image_path}")

    model = _get_model()
    results = model(image, verbose=False)

    for result in results:
        boxes = result.boxes.xyxy  # tensor of [x1, y1, x2, y2]
        if len(boxes) > 0:
            # Pick the detection with the highest confidence
            scores = result.boxes.conf
            best_idx = int(scores.argmax())
            x1, y1, x2, y2 = map(int, boxes[best_idx])

            # Clamp to image boundaries
            h, w = image.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            plate_crop = image[y1:y2, x1:x2]
            if plate_crop.size > 0:
                return plate_crop

    # Fallback: return full image for OCR
    return image
```

***

## 2. [image_utils.py](file:///c:/Users/user/OneDrive/Desktop/gategaurdAI/GateGuard-AI-IOT-/app/utils/image_utils.py) (Image Preprocessing Logic)

This file contains image preprocessing which scales up small plate images and applies an adaptive threshold. This significantly boosts the accuracy of EasyOCR.

```python
"""
Image utilities: save uploads, preprocess plate crops.
"""
import os
import shutil
import uuid
import cv2
import numpy as np
from fastapi import UploadFile

IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)


def save_upload(upload_file: UploadFile) -> str:
    """
    Persist an uploaded image to disk with a unique filename.
    Returns the saved file path.
    """
    ext = os.path.splitext(upload_file.filename)[-1] or ".jpg"
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(IMAGES_DIR, unique_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return file_path


def preprocess_plate(image: np.ndarray) -> np.ndarray:
    """
    Improve OCR accuracy by resizing and enhancing the plate crop.
    Steps:
      1. Upscale (2x) so small plates are readable
      2. Convert to greyscale
      3. Apply adaptive threshold to binarise text
    """
    if image is None or image.size == 0:
        return image

    # 1. Upscale
    h, w = image.shape[:2]
    if w < 200:
        scale = 200 / w
        image = cv2.resize(image, (int(w * scale), int(h * scale)),
                           interpolation=cv2.INTER_CUBIC)

    # 2. Greyscale
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image

    # 3. Adaptive threshold
    processed = cv2.adaptiveThreshold(
        grey, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2,
    )
    return processed


def cleanup_image(file_path: str):
    """Remove temporary uploaded image from disk."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass
```

***

## 3. [ocr_service.py](file:///c:/Users/user/OneDrive/Desktop/gategaurdAI/GateGuard-AI-IOT-/app/services/ocr_service.py) (EasyOCR Logic)

This module encapsulates text readout running the parsed bounding box image through `easyocr`.

```python
"""
OCR service using EasyOCR to extract text from a plate image.

The Reader is initialised once (heavy model download on first run, ~100 MB).
"""
import re
import numpy as np
import easyocr

# Singleton reader
_reader = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def _clean_plate_text(raw: str) -> str:
    """
    Normalise OCR output:
    - Uppercase
    - Remove spaces and special characters
    - Keep only alphanumeric (A-Z, 0-9)
    """
    cleaned = raw.upper()
    cleaned = re.sub(r"[^A-Z0-9]", "", cleaned)
    return cleaned


def read_plate(image: np.ndarray) -> str | None:
    """
    Run EasyOCR on a plate image (numpy array) and return the cleaned plate text.
    Returns None if nothing could be read.
    """
    if image is None or image.size == 0:
        return None

    reader = _get_reader()
    allowlist = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    results = reader.readtext(image, detail=1, paragraph=True, allowlist=allowlist)

    if not results:
        return None

    # Combine all detected text segments (handles multi-line plates)
    full_text = " ".join(res[1] for res in results)
    cleaned = _clean_plate_text(full_text)

    return cleaned if cleaned else None
```

***

## 4. Example Integration Pipeline

Here's an example of how you chain the above 3 logic blocks together (extracted from your current [iot_api.py](file:///c:/Users/user/OneDrive/Desktop/gategaurdAI/GateGuard-AI-IOT-/app/api/iot_api.py)):

```python
from plate_detection import detect_plate
from image_utils import preprocess_plate
from ocr_service import read_plate
import cv2

# Provided an already saved image on disk
filename = "images/car_image.jpg"

# 1. Run YOLO object detection targeting the plate
plate_img = detect_plate(filename)

# 2. Run Image Preprocessing (upscale + greyscale + threshold) to optimize for OCR
plate_img_pre = preprocess_plate(plate_img)

# 3. Read processed image via EasyOCR
plate_text = read_plate(plate_img_pre)

# Fallback mechanism: if plate_text is missing, run OCR directly on the raw un-preprocessed whole image
if not plate_text:
    image = cv2.imread(filename)
    plate_text = read_plate(image)

print(f"Extracted plate text: {plate_text}")
```

## Required Dependencies Map
In your new project, to run everything seamlessly, make sure to add these to your `requirements.txt`:
```txt
numpy
opencv-python-headless  # Or simply opencv-python if showing UI
ultralytics             # For YOLOv8
easyocr                 # For optical character recognition
fastapi                 # If migrating full API with endpoints
python-multipart        # Required for endpoints that consume UploadFile via POST request
```
