from app.services.policy_chunking import (
    chunk_policy_document,
    load_policy_document,
)
from app.services.policy_embeddings import (
    embed_policy_chunks,
    load_embedding_model,
)
from app.services.policy_vector_store import (
    build_vector_index,
    search_vector_index,
)


POLICY_PATH = "knowledge/lending_policy.md"


def build_policy_retriever() -> tuple:
    """Build the policy vector index and return its components."""

    policy_text = load_policy_document(POLICY_PATH)

    chunks = chunk_policy_document(policy_text)

    embedded_chunks = embed_policy_chunks(chunks)

    index = build_vector_index(embedded_chunks)

    model = load_embedding_model()

    return index, embedded_chunks, model


def retrieve_policy(
    query: str,
    index,
    embedded_chunks: list[dict],
    model,
    top_k: int = 3,
) -> list[dict]:
    """Retrieve the most relevant policy chunks for a query."""

    query_embedding = model.encode(
        query,
        convert_to_numpy=True,
    )

    return search_vector_index(
        index,
        query_embedding,
        embedded_chunks,
        top_k=top_k,
    )