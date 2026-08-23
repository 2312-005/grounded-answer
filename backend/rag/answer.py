from datetime import date

from backend.rag.evidence import EvidenceResolver
from backend.rag.policy_rules import get_policy_context
from backend.rag.retriever import PolicyRetriever


class AnswerEngine:
    def __init__(self):
        self.retriever = PolicyRetriever()
        self.resolver = EvidenceResolver()

    def get_evidence(
        self,
        question: str,
        claim_date: date,
        top_k: int = 8,
    ) -> list[dict]:
        """Retrieve relevant policy evidence."""
        return self.retriever.retrieve(
            question=question,
            top_k=top_k,
            claim_date=claim_date,
        )

    def get_context(
        self,
        claim_date: date,
    ) -> dict:
        """Get date-dependent policy context."""
        return get_policy_context(claim_date)

    def _needs_date(self, question: str) -> bool:
        """
        Identify questions where the answer may depend on
        a determination date or change-of-circumstances date.
        """

        text = question.lower()

        date_terms = [
            "on what date",
            "as of",
            "determination",
            "determined",
            "claim date",
            "before",
            "after",
            "in 2026",
            "in 2025",
            "in 2024",
            "how many days",
            "report",
            "change of circumstances",
            "effective",
        ]

        return any(
            term in text
            for term in date_terms
        )

    def should_refuse(
        self,
        question: str,
        claim_date: date | None,
        retrieved: list[dict],
        resolved: dict,
    ) -> tuple[bool, str | None]:
        """
        Conservative refusal decision.

        Refusal is based on evidence quality and policy
        resolution, not only semantic similarity.
        """

        if not retrieved:
            return (
                True,
                "No relevant policy evidence was retrieved.",
            )

        best_distance = retrieved[0]["distance"]

        # Very weak semantic match.
        if best_distance > 1.20:
            return (
                True,
                "The retrieved policy evidence is not sufficiently relevant.",
            )

        # If the question clearly needs a date, require one.
        if self._needs_date(question) and claim_date is None:
            return (
                True,
                "A relevant date is required to determine which policy rule applies.",
            )

        # If the resolver found no applicable rule for a
        # clearly policy-oriented question, do not guess.
        applicable_rules = resolved.get(
            "applicable_rules",
            [],
        )

        if not applicable_rules:
            return (
                True,
                "The supplied policy evidence does not establish an applicable rule.",
            )

        return False, None

    def prepare_answer_context(
        self,
        question: str,
        claim_date: date | None,
    ) -> dict:
        """
        Prepare retrieval, policy resolution and refusal
        information for the answer layer.
        """

        retrieval_date = claim_date or date.today()

        retrieved = self.get_evidence(
            question=question,
            claim_date=retrieval_date,
        )

        resolved = self.resolver.resolve(
            question=question,
            claim_date=retrieval_date,
            retrieved_clauses=retrieved,
        )

        refused, reason = self.should_refuse(
            question=question,
            claim_date=claim_date,
            retrieved=retrieved,
            resolved=resolved,
        )

        return {
            "question": question,
            "claim_date": (
                claim_date.isoformat()
                if claim_date
                else None
            ),
            "policy_context": (
                self.get_context(retrieval_date)
            ),
            "retrieved": retrieved,
            "resolved_evidence": resolved,
            "refuse": refused,
            "refusal_reason": reason,
        }


if __name__ == "__main__":
    engine = AnswerEngine()

    question = "What is the earnings disregard?"
    claim_date = date(2026, 4, 15)

    context = engine.prepare_answer_context(
        question=question,
        claim_date=claim_date,
    )

    print("Question:", context["question"])
    print("Claim date:", context["claim_date"])
    print("Refuse:", context["refuse"])
    print("Reason:", context["refusal_reason"])

    print("\nApplicable rules:")

    for rule in context[
        "resolved_evidence"
    ]["applicable_rules"]:
        print(rule)