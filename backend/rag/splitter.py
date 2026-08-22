import re
from dataclasses import dataclass


@dataclass
class PolicyClause:
    clause_id: str
    text: str


CLAUSE_PATTERN = re.compile(
    r"(?m)^\*\*(\d+\.\d+\.\d+)\*\*\s*(.*?)(?=^\*\*\d+\.\d+\.\d+\*\*|\Z)",
    re.DOTALL,
)


def split_into_clauses(policy_text: str) -> list[PolicyClause]:
    """Split the policy manual into numbered provisions."""
    clauses = []

    for match in CLAUSE_PATTERN.finditer(policy_text):
        clause_id = match.group(1)
        text = match.group(2).strip()

        if text:
            clauses.append(
                PolicyClause(
                    clause_id=clause_id,
                    text=text,
                )
            )

    return clauses


if __name__ == "__main__":
    from loader import load_policy

    policy = load_policy()
    clauses = split_into_clauses(policy)

    print(f"Total clauses found: {len(clauses)}")
    print()

    for clause in clauses[:10]:
        print(f"§{clause.clause_id}")
        print(clause.text[:200])
        print("-" * 60)