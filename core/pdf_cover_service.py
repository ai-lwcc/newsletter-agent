import fitz

from django.core.files.base import ContentFile


def generate_pdf_cover_image(campaign):
    if not campaign.pdf_attachment:
        return

    try:
        document = fitz.open(
            campaign.pdf_attachment.path
        )

        if document.page_count == 0:
            document.close()
            return

        page = document[0]

        pixmap = page.get_pixmap(
            matrix=fitz.Matrix(2, 2)
        )

        image_bytes = pixmap.tobytes("png")

        document.close()

        filename = (
            f"campaign_{campaign.id}_cover.png"
        )

        campaign.pdf_cover_image.save(
            filename,
            ContentFile(image_bytes),
            save=True,
        )

    except Exception:
        # Invalid PDF, test PDF,
        # or image generation failure.
        return