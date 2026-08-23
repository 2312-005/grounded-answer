from pathlib import Path

import chromadb

from backend.rag.embeddings import EmbeddingModel
from backend.rag.loader import load_all_documents
from backend.rag.splitter import split_all_documents


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
        """Build the vector index from the complete policy corpus."""

        documents = load_all_documents()
        clauses = split_all_documents(documents)

        ids = [
            f"{clause.source}:{clause.clause_id}"
            for clause in clauses
        ]

        texts = [
            clause.text
            for clause in clauses
        ]

        embeddings = self.embedding_model.embed_texts(texts)

        metadatas = [
            {
                "clause_id": clause.clause_id,
                "source": clause.source,
            }
            for clause in clauses
        ]

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(clauses)


if __name__ == "__main__":
    store = PolicyVectorStore()
    count = store.build_index()

    print(f"Indexed {count} policy clauses.")
    print(f"ChromaDB location: {CHROMA_PATH}")