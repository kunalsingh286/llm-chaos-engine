from pydantic import BaseModel
from typing import List, Optional


class QueryResponse(BaseModel):
    answer: str
    retrieved_chunks: List[str] = []
    model_used: Optional[str] = None
