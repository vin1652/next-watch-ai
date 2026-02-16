import json
from typing import Any, Dict
from next_watch_ai.llm import GroqLLM, extract_first_json
from next_watch_ai.logging_utils import truncate

TASTE_SCHEMA_HINT = """
Return ONLY JSON with keys:

taste_summary: string,
core_signals: [strings],
secondary_signals: [strings],
avoid_signals: [strings],
query_pack: {
  anchors: [strings],
  must_have: [strings],
  should_have: [strings],
  avoid: [strings]
}
"""

def taste_profile(logger, llm: GroqLLM, fingerprints: Dict[str, Dict[str, Any]], content_type: str, extra_specs: str) -> Dict[str, Any]:
    logger.info("[TasteAgent] building taste profile")
    prompt = f"""
You are a film student building a taste profile from the provided titles.
Infer what the viewer consistently likes in:
- authorship/voice
- narrative architecture
- themes/subtext
- style/tone

Content target: {content_type}
User extra specs (must respect): {extra_specs}

Fingerprints (JSON per title):
{json.dumps(fingerprints, ensure_ascii=False)[:16000]}

{TASTE_SCHEMA_HINT}

ONLY output JSON.
"""
    out = llm.chat(prompt, temperature=0.2)
    data = extract_first_json(out)
    logger.info(f"[TasteAgent] taste_summary={truncate(data.get('taste_summary',''), 500)}")
    logger.info(f"[TasteAgent] core_signals={data.get('core_signals', [])[:8]}")
    logger.info(f"[TasteAgent] avoid_signals={data.get('avoid_signals', [])[:8]}")
    return data
