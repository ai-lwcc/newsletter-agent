import logging
from io import BytesIO
from pathlib import Path

import fitz
from django.core.files.base import ContentFile
from PIL import Image


logger = logging.getLogger(__name__)


SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def generate_cover_image_from_file(file_path):
    extension = Path(file_path).suffix.lower()

    logger.info(
        "Starting cover image generation for file type: %s",
        extension,
    )

    if extension == ".pdf":
        document = fitz.open(file_path)

        try:
            if document.page_count == 0:
                logger.warning(
                    "Cover image generation skipped: PDF has no pages."
                )
                return None

            page = document[0]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_bytes = pixmap.tobytes("png")

            logger.info(
                "Cover image generated from PDF first page."
            )

            return image_bytes

        finally:
            document.close()

    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        image = Image.open(file_path)
        image.thumbnail((1200, 1200))

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        logger.info(
            "Cover image generated from uploaded image."
        )

        return buffer.getvalue()

    logger.warning(
        "Cover image generation skipped: unsupported file type %s",
        extension,
    )

    return None


def generate_attachment_cover_image(campaign):
    logger.info(
        "Starting cover image generation for campaign %s.",
        campaign.id,
    )

    try:
        first_attachment = campaign.attachments.first()

        if first_attachment:
            logger.info(
                "Using first campaign attachment %s for campaign %s cover.",
                first_attachment.id,
                campaign.id,
            )

            image_bytes = generate_cover_image_from_file(
                first_attachment.file.path
            )

        elif campaign.primary_attachment:
            logger.info(
                "Using primary attachment for campaign %s cover.",
                campaign.id,
            )

            image_bytes = generate_cover_image_from_file(
                campaign.primary_attachment.path
            )

        else:
            logger.warning(
                "Cover image generation skipped for campaign %s: no attachment found.",
                campaign.id,
            )
            return

        if not image_bytes:
            logger.warning(
                "Cover image generation skipped for campaign %s: no image bytes generated.",
                campaign.id,
            )
            return

        filename = f"campaign_{campaign.id}_cover.png"

        campaign.cover_image.save(
            filename,
            ContentFile(image_bytes),
            save=True,
        )

        logger.info(
            "Cover image saved for campaign %s as %s.",
            campaign.id,
            filename,
        )

    except Exception:
        logger.exception(
            "Cover image generation failed for campaign %s.",
            campaign.id,
        )
        return