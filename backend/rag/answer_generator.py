from datetime import date

import ollama

from backend.rag.evidence import EvidenceResolver
from backend.rag.retriever import PolicyRetriever


MODEL_NAME = "llama3.2:1b-instruct-q3_K_M"


class GroundedAnswerGenerator:
    """
    Generates natural-language answers with Ollama.

    Policy decisions and citations are controlled by the
    Python evidence layer.
    """

    def __init__(self):
        self.model_name = MODEL_NAME

    def generate(
        self,
        question: str,
        claim_date: date,
        evidence: dict,
    ) -> str:
        prompt = self._build_prompt(
            question=question,
            claim_date=claim_date,
            evidence=evidence,
        )

        response = ollama.chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a grounded policy answer writer. "
                        "The application has already determined "
                        "the applicable policy rule. "
                        "Do not change that rule. "
                        "Do not invent citations. "
                        "Do not invent units or time periods."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        answer = response["message"]["content"].strip()

        answer = self._validate_answer(
            answer=answer,
            evidence=evidence,
        )

        return self._add_verified_citations(
            answer=answer,
            evidence=evidence,
        )

    def _build_prompt(
        self,
        question: str,
        claim_date: date,
        evidence: dict,
    ) -> str:
        rules = []

        for rule in evidence.get("applicable_rules", []):
            effective_rule = rule.get("effective_rule")

            rules.append(
                {
                    "topic": rule.get("topic"),
                    "effective_rule": effective_rule,
                    "base_clause": rule.get("base_clause"),
                    "amendment_clause": rule.get(
                        "amendment_clause"
                    ),
                    "transition_clause": rule.get(
                        "transition_clause"
                    ),
                }
            )

        return f"""
Answer the policy question using ONLY the supplied
effective policy decision.

QUESTION:
{question}

DATE:
{claim_date.isoformat()}

EFFECTIVE POLICY DECISION:
{rules}

IMPORTANT RULES:

1. The effective_rule field is the final applicable rule.
2. Never replace an effective value with an older base value.
3. Never invent units, periods, dates, or conditions.
4. For an income_threshold rule, the values are MONTHLY
   income thresholds. Always say "per month", never "per year".
5. For a reporting_period rule, preserve the period in days.
6. For a sanction_percentage rule, preserve the percentage.
7. For an earnings_disregard rule, preserve the monthly amount.
8. Do not perform calculations unless the effective policy
   decision explicitly requires one.
9. Do not create citations.
10. Do not invent clause numbers.

Write a concise answer in 1 to 3 sentences.

Return only the answer.
""".strip()

    def _validate_answer(
        self,
        answer: str,
        evidence: dict,
    ) -> str:
        """
        Prevent an outdated base value or incorrect time unit
        from surviving in the final answer.
        """

        for rule in evidence.get(
            "applicable_rules",
            [],
        ):
            effective_rule = rule.get(
                "effective_rule"
            )

            base_value = rule.get(
                "base_value"
            )

            if not effective_rule:
                continue

            # Prevent the old base value from appearing
            # when an amendment has changed it.
            if (
                base_value
                and effective_rule != base_value
                and base_value in answer
                and str(effective_rule) not in answer
            ):
                return self._deterministic_answer(
                    rule
                )

            # Income thresholds are monthly.
            if rule.get("topic") == "income_threshold":
                answer = answer.replace(
                    "per year",
                    "per month",
                )

                answer = answer.replace(
                    "a year",
                    "a month",
                )

                answer = answer.replace(
                    "annually",
                    "monthly",
                )

        return answer

    def _deterministic_answer(
        self,
        rule: dict,
    ) -> str:
        effective_rule = rule["effective_rule"]

        if rule.get("topic") == "income_threshold":
            return (
                "The applicable monthly income "
                "threshold is "
                f"{effective_rule}."
            )

        return (
            f"The applicable rule is "
            f"{effective_rule}."
        )

    def _add_verified_citations(
        self,
        answer: str,
        evidence: dict,
    ) -> str:
        """
        Append citations directly from the resolved
        evidence rather than trusting the LLM.
        """

        citations = []

        for rule in evidence.get(
            "applicable_rules",
            [],
        ):
            base_clause = rule.get(
                "base_clause"
            )

            amendment_clause = rule.get(
                "amendment_clause"
            )

            transition_clause = rule.get(
                "transition_clause"
            )

            if base_clause:
                citations.append(
                    base_clause
                )

            if amendment_clause:
                citations.append(
                    amendment_clause
                )

            if transition_clause:
                citations.append(
                    transition_clause
                )

        if not citations:
            return answer

        unique_citations = list(
            dict.fromkeys(citations)
        )

        citation_text = (
            "\n\nCitations: "
            + ", ".join(unique_citations)
        )

        return answer + citation_text


def build_test_evidence():
    question = "What is the earnings disregard?"
    claim_date = date(2026, 4, 15)

    retriever = PolicyRetriever()
    resolver = EvidenceResolver()

    retrieved = retriever.retrieve(
        question=question,
        claim_date=claim_date,
        top_k=8,
    )

    return resolver.resolve(
        question=question,
        claim_date=claim_date,
        retrieved_clauses=retrieved,
    )


if __name__ == "__main__":
    generator = GroundedAnswerGenerator()

    question = "What is the earnings disregard?"
    claim_date = date(2026, 4, 15)

    evidence = build_test_evidence()

    print(
        "Generating grounded answer with Ollama..."
    )
    print()

    answer = generator.generate(
        question=question,
        claim_date=claim_date,
        evidence=evidence,
    )

    print("ANSWER:")
    print(answer)