from datetime import date

from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import PolicyVectorStore


class PolicyRetriever:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.store = PolicyVectorStore()

    def retrieve(
        self,
        question: str,
        top_k: int = 8,
        claim_date: date | None = None,
    ) -> list[dict]:
        """
        Retrieve relevant policy clauses.

        claim_date is carried through the retrieval layer so that
        date-aware policy filtering can be applied separately.
        """

        question_embedding = self.embedding_model.embed_text(question)

        results = self.store.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
        )

        retrieved = []

        ids = results["ids"][0]
        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        for clause_id, document, distance, metadata in zip(
            ids,
            documents,
            distances,
            metadatas,
        ):
            retrieved.append(
                {
                    "clause_id": clause_id,
                    "text": document,
                    "distance": distance,
                    "source": metadata["source"],
                    "claim_date": (
                        claim_date.isoformat()
                        if claim_date
                        else None
                    ),
                }
            )

        return retrieved


if __name__ == "__main__":
    retriever = PolicyRetriever()

    results = retriever.retrieve(
        question="What is the earnings disregard?",
        claim_date=date(2026, 4, 15),
    )

    for result in results:
        print()
        print(f"Clause: {result['clause_id']}")
        print(f"Source: {result['source']}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Claim date: {result['claim_date']}")
        print(result["text"][:300])