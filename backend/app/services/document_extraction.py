from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(file_data: bytes) -> str:
    """Extract text from a PDF document."""

    reader = PdfReader(BytesIO(file_data))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages).strip()