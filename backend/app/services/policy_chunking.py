import re
from pathlib import Path


def load_policy_document(path: str) -> str:
    """Load the policy document as UTF-8 text."""
    return Path(path).read_text(encoding="utf-8")


def chunk_policy_document(text: str) -> list[dict[str, str]]:
    """Split the policy document into section-based chunks."""

    sections = re.split(r"(?m)^## ", text)

    chunks = []

    for section in sections[1:]:
        lines = section.strip().splitlines()

        if not lines:
            continue

        title = lines[0].strip()
        content = "\n".join(lines[1:]).strip()

        if not content:
            continue

        chunks.append(
            {
                "section": title,
                "content": content,
            }
        )

    return chunks