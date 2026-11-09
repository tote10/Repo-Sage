import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "repo-sage"
    VERSION: str = "0.1.0"
    REPO_PATH: Path = Path(os.getenv("REPO_PATH", Path(__file__).resolve().parent.parent.parent / "sample_repo"))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "5"))

settings = Settings()
