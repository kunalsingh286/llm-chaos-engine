import time
import uuid

from app.models.ollama_client import OllamaClient
from app.config import settings


class IncidentManager:
    """
    Incident tracking and postmortem generator
    """

    def __init__(self):

        self.llm = OllamaClient()

        self.model = settings.PRIMARY_MODEL

        self.incidents = []

    # -----------------------------

    def create(
        self,
        slo_state,
        applied_policies
    ):

        incident = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "slo_state": slo_state,
            "policies": applied_policies
        }

        incident["postmortem"] = self._postmortem(
            incident
        )

        self.incidents.append(incident)

        return incident

    # -----------------------------

    def _postmortem(self, incident):

        prompt = f"""
You are an SRE writing an incident postmortem.

Incident:
{incident}

Write a concise RCA and improvement plan.
"""

        try:

            return self.llm.generate(
                self.model,
                prompt
            )

        except Exception:

            return "Postmortem generation failed"

    # -----------------------------

    def list(self):

        return self.incidents
