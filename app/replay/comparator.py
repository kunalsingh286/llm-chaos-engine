from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

from app.config import settings


class ReplayComparator:
    """
    Compares baseline vs chaos outputs
    (JSON-safe)
    """

    def __init__(self):

        self.embedder = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

    def similarity(self, a: str, b: str) -> float:

        vecs = self.embedder.encode([a, b])

        sim = cosine_similarity(
            [vecs[0]],
            [vecs[1]]
        )[0][0]

        return float(sim)   # ✅ Force Python float

    def compare(self, base: str, chaos: str):

        sim = self.similarity(base, chaos)

        degraded = bool(sim < 0.7)   # ✅ Force Python bool

        return {
            "similarity": float(sim),
            "degraded": degraded
        }
