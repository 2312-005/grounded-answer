from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_PATH = PROJECT_ROOT / "data" / "documents"

POLICY_PATH = DOCUMENTS_PATH / "policy-manual.md"
AMENDMENT_PATH = DOCUMENTS_PATH / "Amendment No. 2026-01.md"


def load_policy() -> str:
    """Load the original policy manual."""
    if not POLICY_PATH.exists():
        raise FileNotFoundError(
            f"Policy manual not found at: {POLICY_PATH}"
        )

    return POLICY_PATH.read_text(encoding="utf-8")


def load_amendment() -> str:
    """Load the Day 2 policy amendment."""
    if not AMENDMENT_PATH.exists():
        raise FileNotFoundError(
            f"Amendment not found at: {AMENDMENT_PATH}"
        )

    return AMENDMENT_PATH.read_text(encoding="utf-8")


def load_all_documents() -> dict[str, str]:
    """Load every policy document in the corpus."""
    return {
        "policy-manual.md": load_policy(),
        "Amendment No. 2026-01.md": load_amendment(),
    }


if __name__ == "__main__":
    documents = load_all_documents()

    for name, text in documents.items():
        print(f"{name}")
        print(f"Characters: {len(text)}")
        print("-" * 50)