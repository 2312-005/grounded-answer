from pathlib import Path

import chromadb

from backend.rag.embeddings import EmbeddingModel
from backend.rag.loader import load_policy
from backend.rag.splitter import split_into_clauses


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_PATH = PROJECT_ROOT / "chroma_db"

COLLECTION_NAME = "policy_clauses"


class PolicyVectorStore:
    def __init__(self):
        self.embedding_model = EmbeddingModel()

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    def build_index(self) -> int:
        """Create the ChromaDB index from the policy clauses."""
        policy_text = load_policy()
        clauses = split_into_clauses(policy_text)

        ids = [clause.clause_id for clause in clauses]
        documents = [clause.text for clause in clauses]

        embeddings = self.embedding_model.embed_texts(documents)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=[
                {
                    "clause_id": clause.clause_id,
                    "source": "policy-manual.md",
                }
                for clause in clauses
            ],
        )

        return len(clauses)


if __name__ == "__main__":
    store = PolicyVectorStore()
    count = store.build_index()

    print(f"Indexed {count} policy clauses.")
    print(f"ChromaDB location: {CHROMA_PATH}")