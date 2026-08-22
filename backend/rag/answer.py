from backend.rag.retriever import PolicyRetriever


class AnswerEngine:
    def __init__(self):
        self.retriever = PolicyRetriever()

    def get_evidence(
        self,
        question: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Retrieve policy clauses relevant to the question."""
        return self.retriever.retrieve(
            question,
            top_k=top_k,
        )

    def should_refuse(
        self,
        results: list[dict],
    ) -> bool:
        """
        Conservative initial refusal rule.

        This threshold is temporary and will be calibrated
        using our own ten-question evaluation set.
        """
        if not results:
            return True

        best_distance = results[0]["distance"]

        return best_distance > 0.95