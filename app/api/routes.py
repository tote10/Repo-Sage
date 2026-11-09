from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.config import settings
from rag.ask import ask
from rag.search import get_repo_index, clear_index

class AskRequest(BaseModel):
    question: str = Field(min_length=1, description="Question about the repository")
    k: Optional[int] = Field(default=None, ge=1, le=50, description="Number of chunks to retrieve")
    repo_path: Optional[str] = Field(default=None, description="Path to target repository to query")

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

class IndexRequest(BaseModel):
    repo_path: Optional[str] = Field(default=None, description="Filesystem path of repository directory to index")
    force_refresh: bool = Field(default=True, description="Whether to re-index and clear old cache")

class IndexResponse(BaseModel):
    repo_path: str
    chunks_indexed: int
    status: str

router = APIRouter()

@router.get("/")
def root():
    return {"message": "repo-sage API is running", "version": settings.VERSION}

@router.post("/index", response_model=IndexResponse)
def reindex_codebase(payload: Optional[IndexRequest] = None):
    target_path = payload.repo_path if payload and payload.repo_path else str(settings.REPO_PATH)
    target = Path(target_path)
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=400, detail=f"Invalid repository directory: {target_path}")

    # 1. Clear existing index to ensure idempotency
    clear_index(str(target))

    # 2. Extract new chunks and rebuild index
    index = get_repo_index(str(target), force_refresh=True)

    return IndexResponse(
        repo_path=str(target.resolve()),
        chunks_indexed=len(index.chunks),
        status="success"
    )

@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest):
    k = payload.k if payload.k is not None else settings.DEFAULT_TOP_K
    repo_path = payload.repo_path if payload.repo_path else str(settings.REPO_PATH)
    result = ask(payload.question, k=k, repo_path=repo_path)
    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        citations=result["citations"],
        chunks=[CitationChunk(**c) for c in result.get("chunks", [])]
    )

@router.get("/health")
def health():
    return {"status": "ok"}
