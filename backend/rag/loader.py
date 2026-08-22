from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = PROJECT_ROOT / "data" / "documents" / "policy-manual.md"


def load_policy() -> str:
    """Load the complete policy manual as text."""
    if not POLICY_PATH.exists():
        raise FileNotFoundError(
            f"Policy manual not found at: {POLICY_PATH}"
        )

    return POLICY_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    policy = load_policy()

    print(f"Policy loaded successfully.")
    print(f"Characters: {len(policy)}")
    print("\nFirst 500 characters:\n")
    print(policy[:500])