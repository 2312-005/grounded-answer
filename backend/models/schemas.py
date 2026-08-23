from datetime import date

from pydantic import BaseModel


class QuestionContext(BaseModel):
    question: str
    claim_date: date | None = None


class RetrievedClause(BaseModel):
    clause_id: str
    text: str
    distance: float
    source: str


class AnswerResponse(BaseModel):
    answer: str
    citations: list[str]
    refused: bool
    reason: str | None = None