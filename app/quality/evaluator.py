import numpy as np

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.models.ollama_client import OllamaClient


class QualityEvaluator:
    """
    Evaluates LLM outputs for hallucination and groundedness
    """

    def __init__(self):

        self.embedder = SentenceTransformer(
            settings.EMBEDDING_MODEL
        )

        self.judge_llm = OllamaClient()

        self.judge_model = settings.PRIMARY_MODEL

    # ----------------------------------
    # Embedding Similarity
    # ----------------------------------

    def _similarity(self, a: str, b: str) -> float:

        vecs = self.embedder.encode([a, b])

        score = cosine_similarity(
            [vecs[0]],
            [vecs[1]]
        )[0][0]

        return float(score)

    # ----------------------------------
    # Groundedness Check
    # ----------------------------------

    def groundedness_score(
        self,
        answer: str,
        context_chunks: list
    ) -> float:

        if not context_chunks:
            return 0.0

        context = " ".join(context_chunks)

        return self._similarity(answer, context)

    # ----------------------------------
    # LLM-as-Judge
    # ----------------------------------

    def llm_judge(
        self,
        answer: str,
        context_chunks: list,
        question: str
    ) -> float:

        context = "\n".join(context_chunks)

        prompt = f"""
You are an AI evaluator.

Question:
{question}

Context:
{context}

Answer:
{answer}

Task:
Score from 0.0 to 1.0 how well the answer is supported by the context.
Only return a number.
"""

        try:
            response = self.judge_llm.generate(
                self.judge_model,
                prompt
            )

            score = float(
                response.strip().split()[0]
            )

            return max(0.0, min(score, 1.0))

        except Exception:
            return 0.5

    # ----------------------------------
    # Final Evaluation
    # ----------------------------------

    def evaluate(
        self,
        answer: str,
        context_chunks: list,
        question: str
    ) -> dict:

        grounding = self.groundedness_score(
            answer,
            context_chunks
        )

        judge = self.llm_judge(
            answer,
            context_chunks,
            question
        )

        hallucinated = (
            grounding < 0.4 and judge < 0.5
        )

        return {
            "groundedness": grounding,
            "judge_score": judge,
            "hallucinated": hallucinated
        }
