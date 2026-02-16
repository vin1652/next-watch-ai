from __future__ import annotations
from typing import Any, Dict, List, Optional, TypedDict, Literal

Action = Literal["accept", "revise_candidates", "revise_curation", "answer_question"]

class WatchState(TypedDict, total=False):
    # inputs
    content_type: str
    seed_titles: List[str]
    extra_specs: str

    # intermediate artifacts
    research: Dict[str, str]
    fingerprints: Dict[str, Dict[str, Any]]
    taste: Dict[str, Any]
    candidates: List[str]
    curated: Dict[str, Any]
    cards: Dict[str, Any]

    # agentic control
    critic_feedback: str
    controller_action: Action
    controller_rationale: str
    iterations: int
    max_iters: int

    # conversational follow-up
    user_question: Optional[str]
    answer: Optional[str]