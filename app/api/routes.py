from typing import List, Optional, Dict, Any
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.core.config import settings
from rag.ask import ask
from rag.search import get_repo_index, clear_index
from rag.agent_turn import run_agent_round_trip, StructuredAnswer, SourceRef, ToolCallRecord

class AskRequest(BaseModel):
    question: str = Field(min_length=1, description="Question about the repository")
    k: Optional[int] = Field(default=None, ge=1, le=50, description="Number of chunks to retrieve")
    repo_path: Optional[str] = Field(default=None, description="Path to target repository to query")
    use_tools: bool = Field(default=False, description="Whether to route through tool-enabled agent turn")

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
    sources: Optional[List[SourceRef]] = None
    confidence: Optional[float] = 1.0
    tool_calls: Optional[List[ToolCallRecord]] = None
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

    if payload.use_tools:
        agent_res: StructuredAnswer = run_agent_round_trip(payload.question, repo_path=repo_path)
        citations = [s.citation or f"{s.file}:{s.line}" for s in agent_res.sources if s.citation or s.line]
        return AskResponse(
            question=payload.question,
            answer=agent_res.answer,
            citations=citations,
            sources=agent_res.sources,
            confidence=agent_res.confidence,
            tool_calls=agent_res.tool_calls,
            chunks=[]
        )

    result = ask(payload.question, k=k, repo_path=repo_path)
    sources = [SourceRef(**s) for s in result.get("sources", [])]
    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        citations=result["citations"],
        sources=sources,
        confidence=result.get("confidence", 1.0),
        chunks=[CitationChunk(**c) for c in result.get("chunks", [])]
    )

@router.get("/health")
def health():
    return {"status": "ok"}
