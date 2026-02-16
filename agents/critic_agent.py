import json
from typing import Any, Dict, List
from next_watch_ai.llm import GroqLLM, extract_first_json
from next_watch_ai.logging_utils import truncate

CRITIC_SCHEMA = """
Return ONLY JSON:
{
  "verdict": "pass"|"fail",
  "issues": [string],
  "must_fix": [string],
  "suggested_prompt_patch": string
}
"""

def critique(logger, llm: GroqLLM, content_type: str, extra_specs: str,
             seed_titles: List[str], taste: Dict[str, Any],
             curated: Dict[str, Any], cards: Dict[str, Any]) -> Dict[str, Any]:
    logger.info("[CriticAgent] evaluating recommendations vs constraints")

    prompt = f"""
You are a critic for a recommender system.

Target type: {content_type}
User extra specs (hard constraints): {extra_specs}
Seed titles (do not recommend): {seed_titles}

Taste profile:
{json.dumps(taste, ensure_ascii=False)}

Curated picks:
{json.dumps(curated, ensure_ascii=False)}

Explanation cards:
{json.dumps(cards, ensure_ascii=False)}

Evaluate:
- Do picks match content_type? (movie/tv/both)
- Do picks respect extra_specs? (e.g., avoid action, specific character types etc.)
- Are explanations spoiler-free ?
- Is the set varied enough but still aligned with user requirements?

If failing, propose a short suggested_prompt_patch that we can feed to candidate/curator to fix.

{CRITIC_SCHEMA}

ONLY output JSON.
"""
    out = llm.chat(prompt, temperature=0.2)
    data = extract_first_json(out)
    logger.info(f"[CriticAgent] verdict={data.get('verdict')} issues={data.get('issues', [])[:4]}")
    return data