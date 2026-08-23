from datetime import date

from backend.rag.policy_rules import get_policy_context
from backend.rag.retriever import PolicyRetriever


class AnswerEngine:
    def __init__(self):
        self.retriever = PolicyRetriever()

    def get_evidence(
        self,
        question: str,
        claim_date: date,
        top_k: int = 8,
    ) -> list[dict]:
        """Retrieve policy evidence for a dated question."""
        return self.retriever.retrieve(
            question=question,
            top_k=top_k,
            claim_date=claim_date,
        )

    def get_context(
        self,
        claim_date: date,
    ) -> dict:
        """Get the date-dependent policy context."""
        return get_policy_context(claim_date)

    def should_refuse(
        self,
        results: list[dict],
    ) -> bool:
        """
        Conservative initial refusal rule.

        This remains temporary until we build and evaluate
        the required ten-question test set.
        """
        if not results:
            return True

        best_distance = results[0]["distance"]

        return best_distance > 0.95

    def prepare_answer_context(
        self,
        question: str,
        claim_date: date,
    ) -> dict:
        """
        Prepare everything the future answer generator needs.

        The LLM will later receive this evidence and must not
        use information outside it.
        """
        evidence = self.get_evidence(
            question=question,
            claim_date=claim_date,
        )

        policy_context = self.get_context(claim_date)

        return {
            "question": question,
            "claim_date": claim_date.isoformat(),
            "policy_context": policy_context,
            "evidence": evidence,
            "refuse": self.should_refuse(evidence),
        }


if __name__ == "__main__":
    engine = AnswerEngine()

    context = engine.prepare_answer_context(
        question="What is the earnings disregard?",
        claim_date=date(2026, 4, 15),
    )

    print("Question:", context["question"])
    print("Claim date:", context["claim_date"])
    print("Policy context:", context["policy_context"])
    print("Refuse:", context["refuse"])

    print("\nRetrieved evidence:")

    for item in context["evidence"]:
        print(
            f"\n{item['clause_id']} "
            f"({item['source']})"
        )
        print(item["text"][:250])