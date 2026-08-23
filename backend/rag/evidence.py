from datetime import date


AMENDMENT_EFFECTIVE_DATE = date(2026, 3, 1)

POLICY_SOURCE = "policy-manual.md"
AMENDMENT_SOURCE = "Amendment No. 2026-01.md"


class EvidenceResolver:
    """
    Resolves retrieved policy evidence.

    Amendment-specific rules are resolved explicitly because
    their effective values depend on the claim/determination date.

    General policy questions are resolved from retrieved
    policy clauses without hardcoding the 12 policy sections.
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

        # --------------------------------------------------
        # Separate policy and amendment evidence
        # --------------------------------------------------

        for clause in retrieved_clauses:

            source = clause.get("source", "")

            if source == POLICY_SOURCE:
                evidence["base_clauses"].append(clause)

            elif source == AMENDMENT_SOURCE:
                evidence["amendment_clauses"].append(clause)

        # --------------------------------------------------
        # Date-sensitive amendment rules
        # --------------------------------------------------

        topics = self._detect_amended_topics(question)

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

        if "income_threshold" in topics:
            self._add_income_threshold_rule(
                evidence,
                claim_date,
            )

        # --------------------------------------------------
        # General policy questions
        # --------------------------------------------------

        if not evidence["applicable_rules"]:

            self._add_general_policy_rules(
                evidence,
                question,
            )

        return evidence

    # ======================================================
    # AMENDED TOPIC DETECTION
    # ======================================================

    def _detect_amended_topics(
        self,
        question: str,
    ) -> set[str]:

        text = question.lower()

        topics = set()

        if any(
            phrase in text
            for phrase in [
                "earnings disregard",
                "income disregard",
                "earnings ignored",
                "income ignored",
                "how much of my earnings",
                "how much earnings",
            ]
        ):
            topics.add("earnings_disregard")

        if any(
            phrase in text
            for phrase in [
                "sanction percentage",
                "sanction rate",
                "sanction",
                "percentage deducted",
                "percentage reduction",
            ]
        ):
            topics.add("sanction_percentage")

        if any(
            phrase in text
            for phrase in [
                "reporting period",
                "report a change",
                "reporting a change",
                "report a change of circumstances",
                "change of circumstances",
                "how many days",
                "within how many days",
                "how long do i have to report",
                "when do i have to report",
            ]
        ):
            topics.add("reporting_period")

        if (
            "income threshold" in text
            or "income thresholds" in text
            or "monthly threshold" in text
            or "income limit" in text
        ):
            topics.add("income_threshold")

        return topics

    # ======================================================
    # GENERAL POLICY RESOLUTION
    # ======================================================

    def _add_general_policy_rules(
        self,
        evidence: dict,
        question: str,
    ) -> None:

        clauses = evidence.get(
            "base_clauses",
            [],
        )

        if not clauses:
            return

        selected = self._select_relevant_clauses(
            question,
            clauses,
        )

        for clause in selected:

            clause_id = clause.get(
                "clause_id",
                "",
            )

            text = clause.get(
                "text",
                "",
            )

            if not text:
                continue

            evidence["applicable_rules"].append(
                {
                    "topic": "general_policy",
                    "base_clause": self._section_from_clause_id(
                        clause_id
                    ),
                    "base_text": text,
                    "base_value": None,
                    "amendment_clause": None,
                    "transition_clause": None,
                    "effective_rule": text,
                }
            )

    # ======================================================
    # GENERAL RELEVANCE CHECK
    # ======================================================

    def _select_relevant_clauses(
        self,
        question: str,
        clauses: list[dict],
    ) -> list[dict]:

        if not clauses:
            return []

        question_terms = self._question_terms(
            question
        )

        if not question_terms:
            return []

        # --------------------------------------------------
        # Generic attribute requirements
        # --------------------------------------------------

        question_lower = question.lower()

        attribute_terms = []

        if "maximum age" in question_lower:
            attribute_terms.extend(
                ["maximum", "age"]
            )

        if "minimum age" in question_lower:
            attribute_terms.extend(
                ["minimum", "age"]
            )

        if "maximum amount" in question_lower:
            attribute_terms.extend(
                ["maximum", "amount"]
            )

        if "minimum amount" in question_lower:
            attribute_terms.extend(
                ["minimum", "amount"]
            )

        if "percentage" in question_lower:
            attribute_terms.append(
                "percentage"
            )

        if "days" in question_lower:
            attribute_terms.append(
                "days"
            )

        scored = []

        for clause in clauses:

            text = clause.get(
                "text",
                "",
            )

            if not text:
                continue

            text_lower = text.lower()

            # --------------------------------------------------
            # Attribute evidence check
            # --------------------------------------------------

            if attribute_terms:

                if not all(
                    term in text_lower
                    for term in attribute_terms
                ):
                    continue

            # --------------------------------------------------
            # Normal question-term matching
            # --------------------------------------------------

            matched = []

            for term in question_terms:

                if term in text_lower:
                    matched.append(term)

            matched = list(
                dict.fromkeys(matched)
            )

            if not matched:
                continue

            score = len(matched)

            scored.append(
                {
                    "score": score,
                    "distance": clause.get(
                        "distance",
                        999,
                    ),
                    "clause": clause,
                    "matched": matched,
                }
            )

        if not scored:
            return []

        scored.sort(
            key=lambda item: (
                -item["score"],
                item["distance"],
            )
        )

        best_score = scored[0]["score"]

        # Strong lexical support.
        if best_score >= 3:

            minimum_score = best_score

        # Two meaningful terms require very strong
        # semantic retrieval.
        elif best_score == 2:

            if scored[0]["distance"] <= 1.05:
                minimum_score = 2
            else:
                return []

        else:
            return []

        selected = []

        for item in scored:

            if item["score"] < minimum_score:
                continue

            selected.append(
                item["clause"]
            )

            if len(selected) >= 3:
                break

        return selected

    # ======================================================
    # QUESTION TERM EXTRACTION
    # ======================================================

    def _question_terms(
        self,
        question: str,
    ) -> list[str]:

        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "of",
            "for",
            "to",
            "does",
            "do",
            "did",
            "can",
            "may",
            "how",
            "many",
            "much",
            "who",
            "when",
            "where",
            "which",
            "with",
            "on",
            "in",
            "into",
            "from",
            "have",
            "has",
            "had",
            "will",
            "would",
            "should",
            "could",
            "please",
            "tell",
            "me",
            "my",
            "your",
            "their",
            "our",
            "i",
            "we",
            "you",
            "this",
            "that",
            "provide",
            "policy",
        }

        terms = []

        for raw_word in question.lower().split():

            word = raw_word.strip(
                ".,?!:;()[]{}\"'"
            )

            if len(word) < 3:
                continue

            if word in stop_words:
                continue

            if word not in terms:
                terms.append(word)

        # --------------------------------------------------
        # Generic word variations
        # --------------------------------------------------

        expanded = []

        for term in terms:

            expanded.append(term)

            # eligibility -> eligible
            if term.endswith("ibility"):
                expanded.append(
                    term[:-7] + "ible"
                )

            # ability -> able
            elif term.endswith("ility"):
                expanded.append(
                    term[:-5] + "ile"
                )

            # words ending in -ity
            elif term.endswith("ity"):
                expanded.append(
                    term[:-3]
                )

            # reporting -> report
            elif (
                term.endswith("ing")
                and len(term) > 5
            ):
                expanded.append(
                    term[:-3]
                )

            # reported -> report
            elif (
                term.endswith("ed")
                and len(term) > 5
            ):
                expanded.append(
                    term[:-2]
                )

            # conditions -> condition
            elif (
                term.endswith("s")
                and len(term) > 4
            ):
                expanded.append(
                    term[:-1]
                )

        return list(
            dict.fromkeys(expanded)
        )

    # ======================================================
    # CLAUSE / CITATION HELPERS
    # ======================================================

    def _section_from_clause_id(
        self,
        clause_id: str,
    ) -> str:

        if ":" not in clause_id:
            return clause_id

        section = clause_id.rsplit(
            ":",
            1,
        )[1]

        return f"§{section}"

    def _find_clause(
        self,
        clauses: list[dict],
        clause_id: str,
    ) -> dict | None:

        for clause in clauses:

            if clause.get(
                "clause_id"
            ) == clause_id:
                return clause

        return None

    # ======================================================
    # EARNINGS DISREGARD
    # ======================================================

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
                "base_clause": "§6.4.1",
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

    # ======================================================
    # SANCTION PERCENTAGE
    # ======================================================

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

    # ======================================================
    # REPORTING PERIOD
    # ======================================================

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

    # ======================================================
    # INCOME THRESHOLD
    # ======================================================

    def _add_income_threshold_rule(
        self,
        evidence: dict,
        determination_date: date,
    ) -> None:

        thresholds = self.get_income_thresholds(
            determination_date
        )

        evidence["applicable_rules"].append(
            {
                "topic": "income_threshold",
                "base_clause": "§6.6.1",
                "base_value": None,
                "amendment_clause": thresholds.get(
                    "source"
                ),
                "transition_clause": thresholds.get(
                    "transition"
                ),
                "effective_rule": thresholds,
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


# ==========================================================
# MANUAL TEST
# ==========================================================

if __name__ == "__main__":

    from backend.rag.retriever import PolicyRetriever

    retriever = PolicyRetriever()
    resolver = EvidenceResolver()

    test_questions = [
        "What is the monthly income threshold for a household of 3?",
        "What is the residence condition?",
        "What are the basic eligibility conditions?",
        "What is the maximum age of a vehicle a household may own?",
        "Does the policy provide assistance for overseas holidays?",
    ]

    claim_date = date(2026, 4, 15)

    for question in test_questions:

        print()
        print("=" * 70)
        print("QUESTION:", question)

        retrieved = retriever.retrieve(
            question=question,
            claim_date=claim_date,
        )

        evidence = resolver.resolve(
            question=question,
            claim_date=claim_date,
            retrieved_clauses=retrieved,
        )

        print()
        print("Applicable rules:")

        for rule in evidence[
            "applicable_rules"
        ]:
            print(rule)