from typing import Dict, Any, List
from next_watch_ai.llm import GroqLLM
from next_watch_ai.firecrawl_utils import make_firecrawl
from agents.research_agent import research_one
from agents.fingerprint_agent import fingerprint_one
from agents.taste_agent import taste_profile
from agents.candidate_agent import propose_candidates
from agents.curator_agent import curate
from agents.explanation_agent import explain

def run_pipeline(logger, settings, content_type: str, seed_titles: List[str], extra_specs: str) -> Dict[str, Any]:
    llm = GroqLLM(api_key=settings.groq_api_key, model=settings.groq_model)
    firecrawl = make_firecrawl(settings.firecrawl_api_key)

    # 1) Research
    research: Dict[str, str] = {}
    for t in seed_titles:
        research[t] = research_one(logger, llm, firecrawl, t, content_type, max_pages=3)

    # 2) Fingerprints
    fingerprints: Dict[str, Any] = {}
    for t in seed_titles:
        evidence = research.get(t, "")
        if evidence and len(evidence) >= 400:
            fingerprints[t] = fingerprint_one(logger, llm, t, content_type, evidence)
        else:
            logger.warning(f"[Pipeline] Not enough evidence for fingerprint: {t}")

    # 3) Taste profile (uses fingerprints + user extra specs)
    taste = taste_profile(logger, llm, fingerprints, content_type, extra_specs)

    # 4) Candidate pool (Groq-only)
    candidates = propose_candidates(logger, llm, taste, seed_titles, content_type, extra_specs, n=30)

    # 5) Curate 5 (no ranking)
    curated = curate(logger, llm, taste, candidates, seed_titles, content_type, extra_specs)

    # 6) Explain
    cards = explain(logger, llm, taste, curated, content_type, extra_specs)

    return {
        "research": research,
        "fingerprints": fingerprints,
        "taste": taste,
        "candidates": candidates,
        "curated": curated,
        "cards": cards,
    }
