import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    firecrawl_api_key: str
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"#"llama-3.3-70b-versatile"
    log_level: str = "INFO"

def load_settings() -> Settings:
    firecrawl = os.getenv("FIRECRAWL_API_KEY", "").strip()
    groq = os.getenv("GROQ_API_KEY", "").strip()
    if not firecrawl:
        raise RuntimeError("Missing FIRECRAWL_API_KEY in environment (.env).")
    if not groq:
        raise RuntimeError("Missing GROQ_API_KEY in environment (.env).")

    return Settings(
        firecrawl_api_key=firecrawl,
        groq_api_key=groq,
        groq_model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip(),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
    )
