from datetime import date
import re

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

        # Income thresholds are authoritative structured data.
        # Handle them deterministically so the LLM cannot
        # calculate the wrong household value.
        income_rule = self._get_income_threshold_rule(
            evidence
        )

        if income_rule:
            answer = self._deterministic_income_answer(
                question,
                income_rule,
            )

            return self._add_verified_citations(
                answer=answer,
                evidence=evidence,
            )

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

    def _get_income_threshold_rule(
        self,
        evidence: dict,
    ) -> dict | None:

        for rule in evidence.get(
            "applicable_rules",
            [],
        ):
            if rule.get("topic") != "income_threshold":
                continue

            effective_rule = rule.get(
                "effective_rule"
            )

            if isinstance(effective_rule, dict):
                return rule

        return None

    def _extract_household_size(
        self,
        question: str,
    ) -> int | None:

        text = question.lower()

        number_words = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }

        # Numeric forms:
        # household of 4
        # family of 2
        # household size 5
        numeric_patterns = [
            r"household\s+of\s+(\d+)",
            r"family\s+of\s+(\d+)",
            r"household\s+size\s*(?:of)?\s*(\d+)",
            r"family\s+size\s*(?:of)?\s*(\d+)",
        ]

        for pattern in numeric_patterns:
            match = re.search(
                pattern,
                text,
            )

            if match:
                return int(match.group(1))

        # Word forms:
        # household of four
        # family of two
        # household size of five
        word_pattern = (
            r"(?:household|family)"
            r"(?:\s+size)?"
            r"\s+of\s+"
            r"(one|two|three|four|five|six|seven|eight|nine|ten)"
        )

        match = re.search(
            word_pattern,
            text,
        )

        if match:
            return number_words[
                match.group(1)
            ]

        return None

    def _deterministic_income_answer(
        self,
        question: str,
        rule: dict,
    ) -> str:

        effective_rule = rule.get(
            "effective_rule",
            {},
        )

        household_size = self._extract_household_size(
            question
        )

        if household_size is None:
            return (
                "The applicable monthly income "
                "threshold is determined by "
                "household size."
            )

        key = str(household_size)

        # Direct household sizes 1 through 5.
        if key in effective_rule:
            amount = effective_rule[key]

            return (
                f"The monthly income threshold "
                f"for a household of "
                f"{household_size} is "
                f"${amount:,} per month."
            )

        # Additional household members.
        if (
            household_size > 5
            and "5" in effective_rule
            and "additional_member" in effective_rule
        ):
            additional_members = (
                household_size - 5
            )

            amount = (
                effective_rule["5"]
                + (
                    additional_members
                    * effective_rule[
                        "additional_member"
                    ]
                )
            )

            return (
                f"The monthly income threshold "
                f"for a household of "
                f"{household_size} is "
                f"${amount:,} per month."
            )

        return (
            "The applicable monthly income "
            "threshold is determined by "
            "household size."
        )

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

IMPORTANT RULES:

1. The effective_rule field is the final applicable rule.
2. Never replace an effective value with an older base value.
3. Never invent units, periods, dates, or conditions.
4. Income thresholds are MONTHLY.
5. Always describe an income threshold as "per month".
6. Never describe an income threshold as "per year".
7. Do not calculate a threshold unless explicitly required.
8. Do not create citations.
9. Do not invent clause numbers.

Write a concise answer in 1 to 3 sentences.

Return only the answer.
""".strip()

    def _validate_answer(
        self,
        answer: str,
        evidence: dict,
    ) -> str:

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

            # Prevent an outdated base value from
            # surviving when an amendment changed it.
            if (
                base_value
                and effective_rule != base_value
                and base_value in answer
                and str(effective_rule) not in answer
            ):
                return self._deterministic_answer(
                    rule
                )

            # Income thresholds are always monthly.
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

        effective_rule = rule.get(
            "effective_rule"
        )

        if rule.get("topic") == "income_threshold":
            return (
                "The applicable monthly income "
                "threshold is determined by "
                "household size."
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