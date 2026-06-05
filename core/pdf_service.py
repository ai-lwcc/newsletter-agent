import fitz


def extract_text_from_pdf(file_path, max_chars=12000):
    document = fitz.open(file_path)
    text_parts = []

    for page in document:
        text_parts.append(page.get_text())

    document.close()

    full_text = "\n".join(text_parts).strip()

    return full_text[:max_chars]