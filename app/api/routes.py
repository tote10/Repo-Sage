from fastapi import APIRouter
from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    question: str=Field(min_length=1, description="The question text to uppercase")
router = APIRouter()

@router.get("/")
def root():
    return{"Hello": "World"}
@router.post("/ask")
def ask_question(payload: AskRequest):
    return{"question": payload.question.upper()}

@router.get("/health")
def health():
    return{"status": "ok"}