from datetime import date

from fastapi import FastAPI
from pydantic import BaseModel

from backend.rag.answer import AnswerEngine
from backend.rag.answer_generator import GroundedAnswerGenerator


app = FastAPI(
    title="Grounded Policy Assistant",
    description="Date-aware policy question answering system",
    version="1.0.0",
)

answer_engine = AnswerEngine()
answer_generator = GroundedAnswerGenerator()


class QuestionRequest(BaseModel):
    question: str
    claim_date: date


@app.get("/")
def root():
    return {
        "name": "Grounded Policy Assistant",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    context = answer_engine.prepare_answer_context(
        question=request.question,
        claim_date=request.claim_date,
    )

    if context["refuse"]:
        return {
            "question": request.question,
            "claim_date": request.claim_date.isoformat(),
            "refused": True,
            "reason": context["refusal_reason"],
            "answer": None,
            "citations": [],
        }

    evidence = context["resolved_evidence"]

    answer = answer_generator.generate(
        question=request.question,
        claim_date=request.claim_date,
        evidence=evidence,
    )

    citations = []

    for rule in evidence.get(
        "applicable_rules",
        [],
    ):
        for field in [
            "base_clause",
            "amendment_clause",
            "transition_clause",
        ]:
            citation = rule.get(field)

            if citation and citation not in citations:
                citations.append(citation)

    return {
        "question": request.question,
        "claim_date": request.claim_date.isoformat(),
        "refused": False,
        "reason": None,
        "answer": answer,
        "citations": citations,
        "evidence": evidence,
    }