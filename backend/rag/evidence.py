from datetime import date


AMENDMENT_EFFECTIVE_DATE = date(2026, 3, 1)


class EvidenceResolver:
    """
    Resolves retrieved policy evidence against the
    Day 2 amendment rules.
    """

    def __init__(self):
        self.effective_date = AMENDMENT_EFFECTIVE_DATE

    def resolve(
        self,
        question: str,
        claim_date: date,
        retrieved_clauses: list[dict],
    ) -> dict:
        evidence = {
            "question": question,
            "claim_date": claim_date.isoformat(),
            "base_clauses": [],
            "amendment_clauses": [],
            "applicable_rules": [],
        }

        for clause in retrieved_clauses:
            source = clause.get("source", "")

            if source == "policy-manual.md":
                evidence["base_clauses"].append(clause)

            elif source == "Amendment No. 2026-01.md":
                evidence["amendment_clauses"].append(clause)

        topics = self._detect_topics(question)

        if "earnings_disregard" in topics:
            self._add_earnings_rule(
                evidence,
                claim_date,
            )

        if "sanction_percentage" in topics:
            self._add_sanction_rule(
                evidence,
                claim_date,
            )

        if "reporting_period" in topics:
            self._add_reporting_rule(
                evidence,
                claim_date,
            )

        return evidence

    def _detect_topics(self, question: str) -> set[str]:
        text = question.lower()

        topics = set()

        if any(
            phrase in text
            for phrase in [
                "earnings disregard",
                "income disregard",
                "earnings",
                "disregarded",
            ]
        ):
            topics.add("earnings_disregard")

        if any(
            phrase in text
            for phrase in [
                "sanction",
                "sanction percentage",
                "sanction rate",
            ]
        ):
            topics.add("sanction_percentage")

        if any(
            phrase in text
            for phrase in [
                "reporting period",
                "report a change",
                "reporting a change",
                "change of circumstances",
                "how many days",
                "within how many days",
            ]
        ):
            topics.add("reporting_period")

        return topics

    def _find_clause(
        self,
        clauses: list[dict],
        clause_id: str,
    ) -> dict | None:
        for clause in clauses:
            if clause.get("clause_id") == clause_id:
                return clause

        return None

    def _add_earnings_rule(
        self,
        evidence: dict,
        determination_date: date,
    ) -> None:
        base_clause = self._find_clause(
            evidence["base_clauses"],
            "policy-manual.md:6.4.1",
        )

        if determination_date >= self.effective_date:
            value = "$175 per month"
            amendment = "Amendment §1.1"
            transition = "Amendment §5.1"
        else:
            value = "$120 per month"
            amendment = None
            transition = None

        evidence["applicable_rules"].append(
            {
                "topic": "earnings_disregard",
                "base_clause": "§6.4.1(a)",
                "base_text": (
                    base_clause["text"]
                    if base_clause
                    else None
                ),
                "base_value": "$120 per month",
                "amendment_clause": amendment,
                "transition_clause": transition,
                "effective_rule": value,
            }
        )

    def _add_sanction_rule(
        self,
        evidence: dict,
        determination_date: date,
    ) -> None:
        base_clause = self._find_clause(
            evidence["base_clauses"],
            "policy-manual.md:10.5.2",
        )

        if determination_date >= self.effective_date:
            value = "15 per cent"
            amendment = "Amendment §4.1"
            transition = "Amendment §5.1"
        else:
            value = "20 per cent"
            amendment = None
            transition = None

        evidence["applicable_rules"].append(
            {
                "topic": "sanction_percentage",
                "base_clause": "§10.5.2",
                "base_text": (
                    base_clause["text"]
                    if base_clause
                    else None
                ),
                "base_value": "20 per cent",
                "amendment_clause": amendment,
                "transition_clause": transition,
                "effective_rule": value,
            }
        )

    def _add_reporting_rule(
        self,
        evidence: dict,
        change_date: date,
    ) -> None:
        base_clause = self._find_clause(
            evidence["base_clauses"],
            "policy-manual.md:4.3.2",
        )

        if change_date >= self.effective_date:
            value = "14 calendar days"
            amendment = "Amendment §2.1"
            transition = "Amendment §5.2"
        else:
            value = "10 calendar days"
            amendment = None
            transition = None

        evidence["applicable_rules"].append(
            {
                "topic": "reporting_period",
                "base_clause": "§4.3.2",
                "base_text": (
                    base_clause["text"]
                    if base_clause
                    else None
                ),
                "base_value": "10 calendar days",
                "amendment_clause": amendment,
                "transition_clause": transition,
                "effective_rule": value,
            }
        )

    def get_income_thresholds(
        self,
        determination_date: date,
    ) -> dict:
        if determination_date >= self.effective_date:
            return {
                "1": 1225,
                "2": 1650,
                "3": 2075,
                "4": 2500,
                "5": 2925,
                "additional_member": 425,
                "source": "Amendment §3.1",
                "transition": "Amendment §5.1",
            }

        return {
            "source": "§6.6.1",
            "transition": None,
        }


if __name__ == "__main__":
    from backend.rag.retriever import PolicyRetriever

    retriever = PolicyRetriever()
    resolver = EvidenceResolver()

    question = "What is the earnings disregard?"
    claim_date = date(2026, 4, 15)

    retrieved = retriever.retrieve(
        question=question,
        claim_date=claim_date,
    )

    evidence = resolver.resolve(
        question=question,
        claim_date=claim_date,
        retrieved_clauses=retrieved,
    )

    print("Question:", evidence["question"])
    print("Claim date:", evidence["claim_date"])

    print("\nApplicable rules:")

    for rule in evidence["applicable_rules"]:
        print(rule)