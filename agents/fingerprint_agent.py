from typing import Any, Dict
from next_watch_ai.llm import GroqLLM, extract_first_json
from next_watch_ai.logging_utils import truncate

FINGERPRINT_SCHEMA_HINT = """
Return ONLY JSON with these keys:

authorship_voice: {
  director_style: [strings],
  screenwriter_style: [strings],
  cinematography_style: [strings],
  editing_style: [strings]
},

narrative_architecture: {
  structure_type: string,
  inciting_incident_timing: "early"|"mid"|"late"|null,
  pacing: "slow"|"moderate"|"fast"|null,
  ending_type: "ambiguous"|"resolved"|"ironic"|"circular"|null,
  conflict_type: "internal"|"external"|"mixed"|null
},

themes_subtext: {
  primary_themes: [strings],
  motifs: [strings],
  worldview: "bleak"|"hopeful"|"mixed"|null,
  moral_stance: "compassionate"|"cynical"|"neutral"|null
},

style_tone: {
  realism_vs_stylized: number,            // 0.0 to 1.0
  humor_style: "none"|"deadpan"|"dark"|"broad"|null,
  dread_style: "psychological"|"cosmic"|"social"|"bodily"|null,
  performance_style: "naturalistic"|"theatrical"|null
},

extras: {
  dialogue_density: "low"|"med"|"high"|null,
  narrative_mode: "linear"|"nonlinear"|"elliptical"|null,
  intensity_curve: "gradual"|"spiky"|"constant"|null
},

confidence: {
  overall: number,
  low_confidence_fields: [strings]
},

non_spoiler_notes: [strings]
"""
'''
def fingerprint_one(logger, llm, title, content_type, evidence):
    prompt = f"""... your existing prompt ..."""
    out = llm.chat(prompt, temperature=0.2)

    try:
        data = extract_first_json(out)
    except ValueError:
        logger.warning("[FingerprintAgent] Model didn't return JSON. Retrying with stricter reformat prompt...")
        fix_prompt = f"""
You MUST output ONLY valid JSON (no prose, no markdown).
Reformat the following into the required JSON schema.

TEXT:
{out}
"""
        out2 = llm.chat(fix_prompt, temperature=0.0)
        data = extract_first_json(out2)

    logger.info(f"[FingerprintAgent] result sample={truncate(str(data), 700)}")
    return data
'''
def fingerprint_one(logger, llm, title, content_type, evidence):
    prompt = f"""
You are a film student and critic analyzing craft and storytelling style.

Analyze this {content_type}: "{title}"

Use the research evidence below to infer style, themes, structure, and authorship.
Do NOT include spoilers.
If uncertain, use null and lower confidence.

EVIDENCE:
{evidence[:9000]}

{FINGERPRINT_SCHEMA_HINT}

ONLY output valid JSON.
"""
