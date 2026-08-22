from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import PolicyVectorStore


class PolicyRetriever:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.store = PolicyVectorStore()

    def retrieve(self, question: str, top_k: int = 5) -> list[dict]:
        """Retrieve the most relevant policy clauses for a question."""

        question_embedding = self.embedding_model.embed_text(question)

        results = self.store.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
        )

        retrieved = []

        ids = results["ids"][0]
        documents = results["documents"][0]
        distances = results["distances"][0]

        for clause_id, document, distance in zip(
            ids,
            documents,
            distances,
        ):
            retrieved.append(
                {
                    "clause_id": clause_id,
                    "text": document,
                    "distance": distance,
                }
            )

        return retrieved


if __name__ == "__main__":
    retriever = PolicyRetriever()

    question = "What are the eligibility requirements for assistance?"

    results = retriever.retrieve(question)

    for result in results:
        print(f"\n§{result['clause_id']}")
        print(f"Distance: {result['distance']:.4f}")
        print(result["text"][:300])