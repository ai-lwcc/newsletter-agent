from pathlib import Path

import fitz
import pytesseract
from PIL import Image


SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def extract_text_from_pdf(file_path, max_chars=12000):
    document = fitz.open(file_path)
    text_parts = []

    for page in document:
        text_parts.append(page.get_text())

    document.close()

    return "\n".join(text_parts).strip()[:max_chars]


def extract_text_from_image(file_path, max_chars=12000):
    image = Image.open(file_path)
    text = pytesseract.image_to_string(
        image,
        lang="eng+chi_tra",
    )

    return text.strip()[:max_chars]


def extract_text_from_campaign_file(file_path, max_chars=12000):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path, max_chars=max_chars)

    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        return extract_text_from_image(file_path, max_chars=max_chars)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )