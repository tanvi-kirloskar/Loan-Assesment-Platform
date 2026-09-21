from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


POLICY_DIRECTORY = Path(__file__).resolve().parents[2] / "policies"


@dataclass(frozen=True)
class PolicyChunk:
    source: str
    section: str
    content: str


def _load_policy_chunks() -> list[PolicyChunk]:
    chunks: list[PolicyChunk] = []

    for path in sorted(POLICY_DIRECTORY.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        sections = re.split(r"(?m)^## ", text)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.splitlines()
            title = lines[0].strip()
            content = "\n".join(lines[1:]).strip()

            if content:
                chunks.append(
                    PolicyChunk(
                        source=path.name,
                        section=title,
                        content=content,
                    )
                )

    return chunks


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2
    }


def retrieve_policy(
    query: str,
    *,
    max_results: int = 3,
) -> list[dict[str, str]]:
    """Retrieve relevant internal policy sections using deterministic local retrieval."""
    if max_results <= 0:
        return []

    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    scored: list[tuple[int, PolicyChunk]] = []

    for chunk in _load_policy_chunks():
        chunk_tokens = _tokens(f"{chunk.section} {chunk.content}")
        score = len(query_tokens & chunk_tokens)

        if score:
            scored.append((score, chunk))

    scored.sort(key=lambda item: (-item[0], item[1].source, item[1].section))

    return [
        {
            "source": chunk.source,
            "section": chunk.section,
            "content": chunk.content,
        }
        for _, chunk in scored[:max_results]
    ]
