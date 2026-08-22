from pydantic import BaseModel


class RetrievedClause(BaseModel):
    clause_id: str
    text: str
    distance: float


class AnswerResponse(BaseModel):
    answer: str
    citations: list[str]
    refused: bool
    reason: str | None = None