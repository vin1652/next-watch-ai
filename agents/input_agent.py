from dataclasses import dataclass
from typing import List, Literal

ContentType = Literal["movie", "tv", "both"]

@dataclass
class UserInput:
    content_type: ContentType
    seeds: List[str]
    extra_specs: str

def normalize_content_type(s: str) -> ContentType:
    s = (s or "").strip().lower()
    if s in ["movie", "movies"]:
        return "movie"
    if s in ["tv", "show", "shows", "tv shows", "tvshow", "tvshows"]:
        return "tv"
    return "both"
