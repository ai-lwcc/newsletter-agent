from pathlib import Path
import logging

import fitz
import pytesseract
from PIL import Image


logger = logging.getLogger(__name__)


SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def extract_text_from_pdf(file_path, max_chars=12000):
    logger.info(
        f"Starting PDF text extraction: {file_path}"
    )

    try:
        document = fitz.open(file_path)
        text_parts = []

        for page in document:
            text_parts.append(page.get_text())

        document.close()

        text = "\n".join(text_parts).strip()[:max_chars]

        logger.info(
            f"PDF extraction complete. Characters extracted: {len(text)}"
        )

        return text

    except Exception:
        logger.exception(
            f"PDF extraction failed: {file_path}"
        )
        raise


def extract_text_from_image(file_path, max_chars=12000):
    logger.info(
        f"Starting OCR extraction: {file_path}"
    )

    try:
        image = Image.open(file_path)

        text = pytesseract.image_to_string(
            image,
            lang="eng+chi_tra",
        )

        text = text.strip()[:max_chars]

        logger.info(
            f"OCR extraction complete. Characters extracted: {len(text)}"
        )

        return text

    except Exception:
        logger.exception(
            f"OCR extraction failed: {file_path}"
        )
        raise


def extract_text_from_campaign_file(file_path, max_chars=12000):
    extension = Path(file_path).suffix.lower()

    logger.info(
        f"Processing campaign file. Type: {extension}"
    )

    if extension == ".pdf":
        return extract_text_from_pdf(
            file_path,
            max_chars=max_chars,
        )

    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        return extract_text_from_image(
            file_path,
            max_chars=max_chars,
        )

    logger.warning(
        f"Unsupported campaign file type: {extension}"
    )

    raise ValueError(
        f"Unsupported file type: {extension}"
    )