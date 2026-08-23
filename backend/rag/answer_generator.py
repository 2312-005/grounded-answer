from datetime import date
import re

import ollama

from backend.rag.evidence import EvidenceResolver
from backend.rag.retriever import PolicyRetriever


MODEL_NAME = "llama3.2:1b-instruct-q3_K_M"


class GroundedAnswerGenerator:
    """
    Generates grounded policy answers.

    Python controls exact policy values.
    Ollama is used only for natural-language answers
    where deterministic formatting is not required.
    """

    def __init__(self):
        self.model_name = MODEL_NAME

    def generate(
        self,
        question: str,
        claim_date: date,
        evidence: dict,
    ) -> str:

        # Exact structured policy values should not be
        # calculated or selected by the language model.
        deterministic = self._deterministic_answer_from_rule(
            question=question,
            evidence=evidence,
        )

        if deterministic:
            return deterministic

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
                        "Do not perform calculations. "
                        "Do not invent citations."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        answer = response["message"]["content"].strip()

        return self._validate_answer(
            answer=answer,
            evidence=evidence,
        )

    def _deterministic_answer_from_rule(
        self,
        question: str,
        evidence: dict,
    ) -> str | None:

        for rule in evidence.get(
            "applicable_rules",
            [],
        ):
            topic = rule.get("topic")

            if topic == "income_threshold":
                return self._income_threshold_answer(
                    question=question,
                    rule=rule,
                )

        return None

    def _income_threshold_answer(
        self,
        question: str,
        rule: dict,
    ) -> str | None:

        effective_rule = rule.get(
            "effective_rule"
        )

        if not isinstance(
            effective_rule,
            dict,
        ):
            return None

        household_size = self._extract_household_size(
            question
        )

        if household_size is None:
            return None

        value = effective_rule.get(
            str(household_size)
        )

        if value is None:
            additional_member = effective_rule.get(
                "additional_member"
            )

            if (
                household_size > 5
                and additional_member is not None
            ):
                value = (
                    effective_rule["5"]
                    + (
                        household_size - 5
                    )
                    * additional_member
                )

        if value is None:
            return None

        return (
            "The monthly income threshold for a "
            f"household of {household_size} is "
            f"${value:,}."
        )

    def _extract_household_size(
        self,
        question: str,
    ) -> int | None:

        match = re.search(
            r"household\s+of\s+(\d+)",
            question.lower(),
        )

        if match:
            return int(match.group(1))

        match = re.search(
            r"household\s+size\s*(?:is|of)?\s*(\d+)",
            question.lower(),
        )

        if match:
            return int(match.group(1))

        return None

    def _build_prompt(
        self,
        question: str,
        claim_date: date,
        evidence: dict,
    ) -> str:

        rules = []

        for rule in evidence.get(
            "applicable_rules",
            [],
        ):
            rules.append(
                {
                    "topic": rule.get("topic"),
                    "effective_rule": rule.get(
                        "effective_rule"
                    ),
                    "base_clause": rule.get(
                        "base_clause"
                    ),
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

The effective_rule field is the final applicable rule.

Do not recalculate the rule.

Do not replace the effective value with the
older base value.

Write a concise answer in 1 to 3 sentences.

Do not create a citation list.
Do not invent clause numbers.
The application will provide verified citations separately.

Return only the answer.
""".strip()

    def _validate_answer(
        self,
        answer: str,
        evidence: dict,
    ) -> str:
        """
        Prevent an outdated base value from surviving
        in the final answer when an amendment changed it.
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

            if isinstance(
                effective_rule,
                dict,
            ):
                continue

            if (
                base_value
                and effective_rule != base_value
                and base_value in answer
                and effective_rule not in answer
            ):
                return self._deterministic_answer(
                    rule
                )

        return answer

    def _deterministic_answer(
        self,
        rule: dict,
    ) -> str:

        effective_rule = rule[
            "effective_rule"
        ]

        return (
            f"The applicable rule is "
            f"{effective_rule}."
        )


def build_test_evidence():

    question = (
        "What is the monthly income threshold "
        "for a household of 3?"
    )

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

    question = (
        "What is the monthly income threshold "
        "for a household of 3?"
    )

    claim_date = date(2026, 4, 15)

    evidence = build_test_evidence()

    print(
        "Generating grounded answer..."
    )

    print()

    answer = generator.generate(
        question=question,
        claim_date=claim_date,
        evidence=evidence,
    )

    print("ANSWER:")
    print(answer)