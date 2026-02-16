from typing import List
import json
from next_watch_ai.llm import GroqLLM, extract_first_json
from next_watch_ai.logging_utils import truncate

DIRECT_CANDIDATES_SCHEMA = """
Return ONLY JSON with:
titles: [strings]  // 30 titles
"""

def propose_candidates(logger, llm: GroqLLM, taste_profile: dict, seed_titles: List[str],
                       content_type: str, extra_specs: str, n: int = 30) -> List[str]:
    logger.info("[CandidateAgent] proposing candidate pool via Groq (no web scraping)")
    prompt = f"""
You are a film/TV recommender with film-student taste.

Target type: {content_type} (movie/tv/both)
User extra specs (must respect): {extra_specs}

Taste profile:
{json.dumps(taste_profile, ensure_ascii=False)}

Seed titles (do NOT include these):
{seed_titles}

Propose {n} candidate titles that match:
- authorship/voice, narrative structure, themes, tone
- spoiler-free reasoning mindset
- include ~70% strong matches and ~30% adjacent stretch picks

Return ONLY JSON.

{DIRECT_CANDIDATES_SCHEMA}
"""
    out = llm.chat(prompt, temperature=0.4)
    data = extract_first_json(out)
    titles = data.get("titles", [])
    if not isinstance(titles, list):
        titles = []

    # Deduplicate preserving order
    seen = set()
    deduped = []
    for t in titles:
        if isinstance(t, str):
            k = t.strip().lower()
            if k and k not in seen and k not in {s.lower() for s in seed_titles}:
                seen.add(k)
                deduped.append(t.strip())

    logger.info(f"[CandidateAgent] candidates={len(deduped)} sample={deduped[:12]}")
    return deduped
