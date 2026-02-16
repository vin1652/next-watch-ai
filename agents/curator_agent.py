import json
from typing import Any, Dict, List
from next_watch_ai.llm import GroqLLM, extract_first_json
from next_watch_ai.logging_utils import truncate

CURATOR_SCHEMA = """
Return ONLY JSON:
{
  "recommendations": [
    {
      "title": string,
      "year": string|null,
      "why_selected": [strings]
    }
  ]
}
"""

def curate(logger, llm: GroqLLM, taste_profile: Dict[str, Any], candidate_pool: List[str],
           seed_titles: List[str], content_type: str, extra_specs: str) -> Dict[str, Any]:
    logger.info("[CuratorAgent] selecting final 5 (no ranking)")
    prompt = f"""
You are a film-student curator. Select 5 recommendations.

Target type: {content_type} (movie/tv/both)
User extra specs (must respect): {extra_specs}

Taste profile:
{json.dumps(taste_profile, ensure_ascii=False)}

Seed titles (do NOT recommend these):
{seed_titles}

Candidate pool:
{candidate_pool[:120]}

Rules:
- Choose 5 titles.
- No ranking, just 5 picks.
- Keep reasoning spoiler-free: craft, tone, themes, narrative style.
- Avoid overly obvious mainstream picks unless perfect.
- Make picks feel varied but aligned with taste.

{CURATOR_SCHEMA}

ONLY output JSON.
"""
    out = llm.chat(prompt, temperature=0.2)
    data = extract_first_json(out)
    logger.info(f"[CuratorAgent] selected sample={truncate(str(data), 900)}")
    return data
