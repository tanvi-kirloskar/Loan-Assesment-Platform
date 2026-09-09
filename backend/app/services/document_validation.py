from pathlib import Path


MAX_FILE_SIZE = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}

FILE_SIGNATURES = {
    ".pdf": b"%PDF",
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
    ".jpeg": b"\xff\xd8\xff",
}


def validate_document(
    filename: str,
    file_data: bytes,
) -> str:
    """Validate document filename, size, and file signature.

    Returns the normalized file extension when validation succeeds.
    Raises ValueError when validation fails.
    """

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Only PDF, PNG, and JPEG files are allowed."
        )

    if not file_data:
        raise ValueError("Uploaded file is empty.")

    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the 5 MB limit.")

    expected_signature = FILE_SIGNATURES[extension]

    if not file_data.startswith(expected_signature):
        raise ValueError(
            "File content does not match the expected file type."
        )

    return extension
