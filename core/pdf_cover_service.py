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


def generate_pdf_cover_image(campaign):
    if not campaign.pdf_attachment:
        return

    file_path = campaign.pdf_attachment.path
    extension = Path(file_path).suffix.lower()

    try:
        if extension == ".pdf":
            document = fitz.open(file_path)

            if document.page_count == 0:
                document.close()
                return

            page = document[0]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image_bytes = pixmap.tobytes("png")

            document.close()

        elif extension in SUPPORTED_IMAGE_EXTENSIONS:
            image = Image.open(file_path)
            image.thumbnail((1200, 1200))

            from io import BytesIO

            buffer = BytesIO()
            image.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()

        else:
            return

        filename = f"campaign_{campaign.id}_cover.png"

        campaign.pdf_cover_image.save(
            filename,
            ContentFile(image_bytes),
            save=True,
        )

    except Exception:
        return