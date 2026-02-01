class FaultInjector:
    def __init__(self):
        self.enabled = False

    def before_retrieval(self, query: str) -> str:
        return query

    def after_retrieval(self, chunks):
        return chunks

    def before_llm(self, prompt: str) -> str:
        return prompt

    def after_llm(self, response: str) -> str:
        return response
