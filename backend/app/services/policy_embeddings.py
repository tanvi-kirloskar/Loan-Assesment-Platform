from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


def load_embedding_model() -> SentenceTransformer:
    """Load the local sentence-transformer embedding model."""
    return SentenceTransformer(MODEL_NAME)


def embed_policy_chunks(chunks: list[dict[str, str]]) -> list[dict]:
    """Generate embeddings for policy chunks."""

    model = load_embedding_model()

    texts = [chunk["content"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
    )

    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings):
        embedded_chunks.append(
            {
                "section": chunk["section"],
                "content": chunk["content"],
                "embedding": embedding,
            }
        )

    return embedded_chunks