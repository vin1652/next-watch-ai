from typing import List
from next_watch_ai.llm import GroqLLM, parse_python_list
from next_watch_ai.firecrawl_utils import scrape_bundle
from next_watch_ai.logging_utils import truncate

def generate_seed_urls(llm: GroqLLM, title: str, content_type: str, max_urls: int = 5) -> List[str]:
    prompt = f"""
You are gathering research sources for film/TV analysis.

Title: {title}
Type: {content_type} (movie/tv/both)

Return up to {max_urls} high-quality URLs that are likely scrape-friendly.

Prefer:
- Wikipedia
- IMDb (only if accessible)
- Rotten Tomatoes / Metacritic pages (only if accessible)
- public review/analysis blogs that are not paywalled

Avoid (often blocked/paywalled):
- The Atlantic
- The New Yorker
- WSJ
- NYTimes
- major paywalled magazines

Return ONLY a Python list of URLs.
"""
    out = llm.chat(prompt, temperature=0)
    urls = [u.strip() for u in parse_python_list(out) if isinstance(u, str) and u.strip().startswith("http")]
    return urls

def research_one(logger, llm: GroqLLM, firecrawl, title: str, content_type: str,
                 max_pages: int = 3) -> str:
    logger.info(f"[ResearchAgent] researching: {title}")
    urls = generate_seed_urls(llm, title, content_type,max_urls=10)
    logger.info(f"[ResearchAgent] urls({len(urls)}): {urls[:max_pages]}")
    if not urls:
        return ""
    bundle = scrape_bundle(firecrawl, urls, logger=logger, max_pages=max_pages)
    logger.info(f"[ResearchAgent] bundle chars={len(bundle)} sample={truncate(bundle, 500)}")
    return bundle
