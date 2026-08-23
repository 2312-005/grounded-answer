from datetime import date

from backend.rag.embeddings import EmbeddingModel
from backend.rag.vector_store import PolicyVectorStore


AMENDMENT_SOURCE = "Amendment No. 2026-01.md"


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

        Normal policy clauses are retrieved semantically.
        Amendment clauses are retrieved separately when the
        question may relate to an amended policy area.
        """

        question_embedding = (
            self.embedding_model.embed_text(question)
        )

        results = self.store.collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
        )

        retrieved = self._format_results(
            results,
            claim_date,
        )

        amendment_results = self._retrieve_amendment_evidence(
            question=question,
            question_embedding=question_embedding,
            claim_date=claim_date,
        )

        retrieved = self._merge_results(
            retrieved,
            amendment_results,
        )

        return retrieved

    def _retrieve_amendment_evidence(
        self,
        question: str,
        question_embedding,
        claim_date: date | None,
    ) -> list[dict]:
        """
        Retrieve amendment clauses separately.

        This prevents important amendment clauses from being
        lost simply because the amendment wording is less
        semantically similar to the user's question.
        """

        results = self.store.collection.query(
            query_embeddings=[question_embedding],
            n_results=20,
            where={
                "source": AMENDMENT_SOURCE,
            },
        )

        return self._format_results(
            results,
            claim_date,
        )

    def _format_results(
        self,
        results: dict,
        claim_date: date | None,
    ) -> list[dict]:
        retrieved = []

        if not results.get("ids"):
            return retrieved

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

    def _merge_results(
        self,
        normal_results: list[dict],
        amendment_results: list[dict],
    ) -> list[dict]:
        """
        Merge normal and amendment evidence without
        duplicating clauses.
        """

        merged = []
        seen = set()

        for result in (
            normal_results + amendment_results
        ):
            clause_id = result["clause_id"]

            if clause_id in seen:
                continue

            seen.add(clause_id)
            merged.append(result)

        return merged


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
        print(
            f"Distance: {result['distance']:.4f}"
        )
        print(
            f"Claim date: {result['claim_date']}"
        )
        print(result["text"][:300])