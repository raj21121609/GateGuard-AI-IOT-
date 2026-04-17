import cv2

def preprocess_plate(image):
    if image is None or image.size == 0:
        return image

    h, w = image.shape[:2]

    # Upscale if small
    if w < 200:
        scale = 200 / w
        image = cv2.resize(image, (int(w * scale), int(h * scale)))

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply threshold
    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return processed