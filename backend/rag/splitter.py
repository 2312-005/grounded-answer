import re
from dataclasses import dataclass


@dataclass
class PolicyClause:
    clause_id: str
    text: str
    source: str


POLICY_CLAUSE_PATTERN = re.compile(
    r"(?m)^\*\*(\d+\.\d+\.\d+)\*\*\s*(.*?)(?=^\*\*\d+\.\d+\.\d+\*\*|\Z)",
    re.DOTALL,
)

AMENDMENT_CLAUSE_PATTERN = re.compile(
    r"(?m)^\*\*(\d+\.\d+)\*\*\s*(.*?)(?=^\*\*\d+\.\d+\*\*|\Z)",
    re.DOTALL,
)


def split_policy_into_clauses(
    policy_text: str,
) -> list[PolicyClause]:
    clauses = []

    for match in POLICY_CLAUSE_PATTERN.finditer(policy_text):
        clauses.append(
            PolicyClause(
                clause_id=match.group(1),
                text=match.group(2).strip(),
                source="policy-manual.md",
            )
        )

    return clauses


def split_amendment_into_clauses(
    amendment_text: str,
) -> list[PolicyClause]:
    clauses = []

    for match in AMENDMENT_CLAUSE_PATTERN.finditer(amendment_text):
        clauses.append(
            PolicyClause(
                clause_id=f"AMENDMENT-{match.group(1)}",
                text=match.group(2).strip(),
                source="Amendment No. 2026-01.md",
            )
        )

    return clauses


def split_all_documents(
    documents: dict[str, str],
) -> list[PolicyClause]:
    clauses = []

    clauses.extend(
        split_policy_into_clauses(
            documents["policy-manual.md"]
        )
    )

    clauses.extend(
        split_amendment_into_clauses(
            documents["Amendment No. 2026-01.md"]
        )
    )

    return clauses


if __name__ == "__main__":
    from backend.rag.loader import load_all_documents

    documents = load_all_documents()
    clauses = split_all_documents(documents)

    print(f"Total clauses found: {len(clauses)}")
    print()

    for clause in clauses[-10:]:
        print(f"{clause.clause_id}")
        print(f"Source: {clause.source}")
        print(clause.text[:250])
        print("-" * 60)