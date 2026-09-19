import faiss
import numpy as np


def build_vector_index(embedded_chunks: list[dict]):
    """Build a FAISS similarity index from embedded policy chunks."""

    vectors = np.array(
        [chunk["embedding"] for chunk in embedded_chunks],
        dtype="float32",
    )

    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    return index


def search_vector_index(
    index,
    query_embedding,
    embedded_chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """Return the most similar policy chunks."""

    query_vector = np.array(
        [query_embedding],
        dtype="float32",
    )

    distances, indices = index.search(
        query_vector,
        top_k,
    )

    results = []

    for distance, index_position in zip(
        distances[0],
        indices[0],
    ):
        if index_position == -1:
            continue

        chunk = embedded_chunks[index_position]

        results.append(
            {
                "section": chunk["section"],
                "content": chunk["content"],
                "distance": float(distance),
            }
        )

    return results