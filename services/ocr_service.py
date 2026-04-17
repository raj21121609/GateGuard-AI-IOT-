import easyocr
import re

_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'], gpu=False)
    return _reader


def clean_text(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text


def read_plate(image):
    if image is None:
        return None

    reader = _get_reader()

    results = reader.readtext(image)

    if not results:
        return None

    text = " ".join([res[1] for res in results])
    return clean_text(text)