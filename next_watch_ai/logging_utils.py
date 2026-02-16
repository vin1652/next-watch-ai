import logging
import os
from datetime import datetime

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    os.makedirs("logs", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join("logs", f"run_{ts}.log")

    logger = logging.getLogger("next_watch_ai")
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, log_level, logging.INFO))
    ch.setFormatter(fmt)

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(getattr(logging, log_level, logging.INFO))
    fh.setFormatter(fmt)

    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info(f"Logging to {log_path}")
    return logger

def truncate(text: str, max_chars: int = 900) -> str:
    if not text:
        return ""
    text = text.strip()
    return text if len(text) <= max_chars else text[:max_chars] + " ...[truncated]"