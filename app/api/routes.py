from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.config import settings
from rag.ask import ask

class AskRequest(BaseModel):
    question: str = Field(min_length=1, description="Question about the repository")
    k: Optional[int] = Field(default=None, ge=1, le=20, description="Number of chunks to retrieve")

class CitationChunk(BaseModel):
    file: str
    start_line: int
    end_line: int
    score: float
    citation: str
    name: Optional[str] = None
    type: Optional[str] = None

class AskResponse(BaseModel):
    question: str
    answer: str
    citations: List[str]
    chunks: Optional[List[CitationChunk]] = None

router = APIRouter()

@router.get("/")
def root():
    return {"message": "repo-sage API is running", "version": settings.VERSION}

@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    k = payload.k if payload.k is not None else settings.DEFAULT_TOP_K
    result = ask(payload.question, k=k, repo_path=str(settings.REPO_PATH))
    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        citations=result["citations"],
        chunks=[CitationChunk(**c) for c in result.get("chunks", [])]
    )

@router.get("/health")
def health():
    return {"status": "ok"}
