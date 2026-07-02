"""Direct AI orchestrator entry points — Q&A, summarization, knowledge retrieval."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.ai.rag import retrieve_relevant
from app.ai.orchestrator import explain_concept
from app.core.deps import CurrentUserDep  # noqa: F401  (auth-gated globally via middleware)

router = APIRouter()


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    vehicle_id: str | None = None
    top_k: int = 6


class AskResponse(BaseModel):
    answer: str
    citations: list[dict]
    model: str


@router.post("/ask", response_model=AskResponse)
async def ask(payload: AskRequest, user: CurrentUserDep) -> AskResponse:
    snippets = await retrieve_relevant(payload.question, k=payload.top_k)
    answer, model = await explain_concept(payload.question, snippets=snippets)
    return AskResponse(
        answer=answer,
        citations=[
            {"source_id": s["source_id"], "snippet": s["text"][:240], "score": s["score"]}
            for s in snippets
        ],
        model=model,
    )
