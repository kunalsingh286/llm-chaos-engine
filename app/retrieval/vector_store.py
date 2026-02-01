import os
from typing import List

import chromadb
from sentence_transformers import SentenceTransformer

from app.config import settings


class VectorStore:
    def __init__(self):
        self.client = chromadb.Client(
            chromadb.config.Settings(
                persist_directory=settings.CHROMA_PATH
            )
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

        self.embedder = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        self._bootstrap()

    def _bootstrap(self):
        """
        Load sample documents on first run
        """

        # If already populated, skip
        if self.collection.count() > 0:
            return

        docs_path = "data/sample_docs.txt"

        if not os.path.exists(docs_path):
            return

        with open(docs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        docs = [l.strip() for l in lines if l.strip()]

        if not docs:
            return

        embeddings = self.embedder.encode(docs).tolist()

        ids = [f"doc_{i}" for i in range(len(docs))]

        self.collection.add(
            documents=docs,
            embeddings=embeddings,
            ids=ids
        )

        # Persistence is automatic in new Chroma versions

    def query(self, text: str, top_k: int = 3) -> List[str]:

        embedding = self.embedder.encode([text]).tolist()

        results = self.collection.query(
            query_embeddings=embedding,
            n_results=top_k
        )

        documents = results.get("documents", [[]])[0]

        return documents
