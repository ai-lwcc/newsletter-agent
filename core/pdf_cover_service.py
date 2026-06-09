from io import BytesIO
from pathlib import Path

import fitz
from django.core.files.base import ContentFile
from PIL import Image


SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}


def generate_cover_image_from_file(file_path):
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        document = fitz.open(file_path)

        if document.page_count == 0:
            document.close()
            return None

        page = document[0]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        image_bytes = pixmap.tobytes("png")

        document.close()

        return image_bytes

    if extension in SUPPORTED_IMAGE_EXTENSIONS:
        image = Image.open(file_path)
        image.thumbnail((1200, 1200))

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        return buffer.getvalue()

    return None


def generate_attachment_cover_image(campaign):
    try:
        first_attachment = campaign.attachments.first()

        if first_attachment:
            image_bytes = generate_cover_image_from_file(
                first_attachment.file.path
            )
        elif campaign.primary_attachment:
            image_bytes = generate_cover_image_from_file(
                campaign.primary_attachment.path
            )
        else:
            return

        if not image_bytes:
            return

        filename = f"campaign_{campaign.id}_cover.png"

        campaign.cover_image.save(
            filename,
            ContentFile(image_bytes),
            save=True,
        )

    except Exception:
        return