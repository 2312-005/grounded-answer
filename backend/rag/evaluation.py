from datetime import date

from backend.rag.answer import AnswerEngine


TEST_CASES = [
    {
        "question": "What is the earnings disregard?",
        "claim_date": date(2026, 4, 15),
        "expected": "$175",
        "should_refuse": False,
    },
    {
        "question": "What is the earnings disregard?",
        "claim_date": date(2026, 2, 15),
        "expected": "$120",
        "should_refuse": False,
    },
    {
        "question": "How many days does a recipient have to report a change of circumstances?",
        "claim_date": date(2026, 4, 15),
        "expected": "14",
        "should_refuse": False,
    },
    {
        "question": "How many days does a recipient have to report a change of circumstances?",
        "claim_date": date(2026, 2, 15),
        "expected": "10",
        "should_refuse": False,
    },
    {
        "question": "What is the sanction percentage?",
        "claim_date": date(2026, 4, 15),
        "expected": "15",
        "should_refuse": False,
    },
    {
        "question": "What is the sanction percentage?",
        "claim_date": date(2026, 2, 15),
        "expected": "20",
        "should_refuse": False,
    },
    {
        "question": "What is the monthly income threshold for a household of 3?",
        "claim_date": date(2026, 4, 15),
        "expected": "2075",
        "should_refuse": False,
    },
    {
        "question": "What is the monthly income threshold for a household of 5?",
        "claim_date": date(2026, 4, 15),
        "expected": "2925",
        "should_refuse": False,
    },
    {
        "question": "What is the maximum age of a vehicle a household may own?",
        "claim_date": date(2026, 4, 15),
        "expected": None,
        "should_refuse": True,
    },
    {
        "question": "Does the policy provide assistance for overseas holidays?",
        "claim_date": date(2026, 4, 15),
        "expected": None,
        "should_refuse": True,
    },
]


def run_evaluation():
    engine = AnswerEngine()

    passed = 0

    print("=" * 70)
    print("GROUNDED POLICY EVALUATION")
    print("=" * 70)

    for index, case in enumerate(TEST_CASES, start=1):
        print(f"\nTest {index}/10")
        print(f"Question: {case['question']}")
        print(f"Claim date: {case['claim_date']}")

        context = engine.prepare_answer_context(
            question=case["question"],
            claim_date=case["claim_date"],
        )

        refused = context["refuse"]

        print(f"Refuse: {refused}")

        test_passed = refused == case["should_refuse"]

        if not refused and case["expected"]:
            rules = context[
                "resolved_evidence"
            ].get("applicable_rules", [])

            effective_rules = [
                str(rule.get("effective_rule", ""))
                for rule in rules
            ]

            combined = " ".join(
                effective_rules
            )

            expected = case["expected"]

            if expected not in combined:
                test_passed = False

            print(
                "Effective rules:",
                effective_rules,
            )

        if case["should_refuse"]:
            print(
                "Refusal reason:",
                context["refusal_reason"],
            )

        if test_passed:
            print("RESULT: PASS")
            passed += 1
        else:
            print("RESULT: FAIL")

    print("\n" + "=" * 70)
    print(
        f"RESULT: {passed}/{len(TEST_CASES)} tests passed"
    )
    print("=" * 70)

    return passed


if __name__ == "__main__":
    run_evaluation()