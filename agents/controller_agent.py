import json
from typing import Any, Dict
from next_watch_ai.llm import GroqLLM, extract_first_json
from next_watch_ai.logging_utils import truncate

CONTROLLER_SCHEMA = """
Return ONLY JSON:
{
  "action": "accept"|"revise_candidates"|"revise_curation"|"answer_question",
  "rationale": string,
  "message_to_user": string
}
"""

def controller(logger, llm: GroqLLM, state: Dict[str, Any]) -> Dict[str, Any]:
    content_type = state.get("content_type")
    extra_specs = state.get("extra_specs", "")
    iters = state.get("iterations", 0)
    max_iters = state.get("max_iters", 2)
    user_question = (state.get("user_question") or "").strip()

    taste = state.get("taste", {})
    curated = state.get("curated", {})
    cards = state.get("cards", {})
    critic = state.get("critic_feedback", "")

    #  classify if the user is asking to change recs vs asking about current recs
    forced_action = None
    if user_question:
        q = user_question.lower()
        wants_new_recs = any(phrase in q for phrase in [
            "new recommendations", "new recs", "more like", "similar to",
            "add", "remove", "exclude", "instead", "different",
            "change the list", "regenerate", "redo", "re-run",
            "make it", "make them", "less", "more", "darker", "lighter", "scarier"
        ])
        if not wants_new_recs:
            forced_action = "answer_question"

    #  don't bias Q&A with critic failures
    critic_for_prompt = "" if forced_action == "answer_question" else critic

    prompt = f"""
You are the controller of an agentic recommender workflow.

You can choose ONE action:
- accept: finish and show results
- revise_candidates: regenerate candidate pool (bigger change)
- revise_curation: reselect final 5 from existing candidates (smaller change)
- answer_question: answer the user's follow-up question using stored artifacts

Critical rules:
- If user_question is present AND it is a question about the existing recommendations (e.g., "why this pick?"),
  you MUST choose action="answer_question". Do NOT choose revise_* just because critic_feedback is "fail".
- Only choose revise_candidates/revise_curation if the user explicitly asks to change the recommendations. DO NOT choose to do revision LIGHTLY only if REQUIRED
  (new constraints, "give me new recs", "make it darker", etc).
- If iterations >= {max_iters}, you must choose "accept" or "answer_question".
- Respect content_type={content_type} and extra_specs="{extra_specs}".
- Do NOT add spoilers.

State summary:
iterations={iters}/{max_iters}
user_question={user_question}

Critic feedback JSON (if any):
{critic_for_prompt}

Taste profile (summary fields):
{json.dumps({
  "taste_summary": taste.get("taste_summary"),
  "core_signals": taste.get("core_signals", [])[:10],
  "avoid_signals": taste.get("avoid_signals", [])[:10],
}, ensure_ascii=False)}

Current picks:
{json.dumps(cards, ensure_ascii=False)}

If answering a user_question:
- directly answer using the "Current picks" and "Taste profile"
- keep it short and non-spoiler

{CONTROLLER_SCHEMA}
ONLY output JSON.
"""

    out = llm.chat(prompt, temperature=0.2)
    data = extract_first_json(out)

    if forced_action:
        data["action"] = forced_action

    logger.info(f"[ControllerAgent] action={data.get('action')} rationale={truncate(data.get('rationale',''), 300)}")
    return data
