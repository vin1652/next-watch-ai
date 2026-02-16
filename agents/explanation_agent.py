import json
from typing import Any, Dict
from next_watch_ai.llm import GroqLLM, extract_first_json
from next_watch_ai.logging_utils import truncate


EXPLAIN_SCHEMA = """
Return ONLY JSON:
{
  "cards": [
    {
      "title": string,
      "year": string|null,
      "why_this_fits": [strings],   // exactly 3 bullets
      "watch_for": string
    }
  ]
}
"""

def explain(logger, llm: GroqLLM, taste_profile: Dict[str, Any], curated: Dict[str, Any],
            content_type: str, extra_specs: str) -> Dict[str, Any]:
    logger.info("[ExplanationAgent] writing spoiler-free cards")
    prompt = f"""
Write spoiler-free recommendation cards.

Target type: {content_type}
User extra specs (must respect): {extra_specs}

Taste profile:
{json.dumps(taste_profile, ensure_ascii=False)}

Selected titles:
{json.dumps(curated, ensure_ascii=False)}

Rules:
- No plot spoilers, no twist mention, no ending description.
- Explain via: authorship/voice, narrative architecture, themes/subtext, style/tone.
- Each card should feel distinct and specific.
- Use EXACTLY 3 bullets in why_this_fits.

{EXPLAIN_SCHEMA}

ONLY output JSON.
"""
    out = llm.chat(prompt, temperature=0.3)
    data = extract_first_json(out)
    logger.info(f"[ExplanationAgent] cards sample={truncate(str(data), 900)}")
    return data
