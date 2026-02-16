# next_watch_ai/graph.py
from __future__ import annotations
from typing import Any, Dict
from langgraph.graph import StateGraph, END

from next_watch_ai.graph_state import WatchState
from next_watch_ai.llm import GroqLLM
from next_watch_ai.firecrawl_utils import make_firecrawl
from agents.research_agent import research_one
from agents.fingerprint_agent import fingerprint_one
from agents.taste_agent import taste_profile
from agents.candidate_agent import propose_candidates
from agents.curator_agent import curate
from agents.explanation_agent import explain
from agents.critic_agent import critique
from agents.controller_agent import controller
import json 


def build_graph(logger, settings):
    llm = GroqLLM(api_key=settings.groq_api_key, model=settings.groq_model)
    firecrawl = make_firecrawl(settings.firecrawl_api_key)

    def n_research(state: WatchState) -> WatchState:
        research = {}
        for t in state["seed_titles"]:
            research[t] = research_one(logger, llm, firecrawl, t, state["content_type"], max_pages=3)
        return {"research": research}

    def n_fingerprint(state: WatchState) -> WatchState:
        fps = {}
        for t in state["seed_titles"]:
            ev = (state.get("research", {}) or {}).get(t, "")
            if ev and len(ev) >= 400:
                fps[t] = fingerprint_one(logger, llm, t, state["content_type"], ev)
        return {"fingerprints": fps}

    def n_taste(state: WatchState) -> WatchState:
        taste = taste_profile(
            logger, llm,
            state.get("fingerprints", {}),
            state["content_type"],
            state.get("extra_specs", "")
        )
        return {"taste": taste}

    def n_candidates(state: WatchState) -> WatchState:
        # big list (30). Only generated when controller explicitly asks to revise candidates.
        #logger.info(f"TASTE LENGTH: {len(json.dumps(state['taste']))}")
        

        cand = propose_candidates(
            logger, llm,
            state["taste"],
            state["seed_titles"],
            state["content_type"],
            state.get("extra_specs", ""),
            n=30
        )
        return {"candidates": cand}

    def n_curate(state: WatchState) -> WatchState:
        # curate from existing candidates; does NOT require new scraping.
        curated = curate(
            logger, llm,
            state["taste"],
            state.get("candidates", []),
            state["seed_titles"],
            state["content_type"],
            state.get("extra_specs", "")
        )
        return {"curated": curated}

    def n_explain(state: WatchState) -> WatchState:
        cards = explain(
            logger, llm,
            state["taste"],
            state["curated"],
            state["content_type"],
            state.get("extra_specs", "")
        )
        #logger.info(f"CARDS LENGTH: {len(json.dumps(state['cards']))}")
        return {"cards": cards}

    def n_critic(state: WatchState) -> WatchState:
        critic_json = critique(
            logger, llm,
            content_type=state["content_type"],
            extra_specs=state.get("extra_specs", ""),
            seed_titles=state["seed_titles"],
            taste=state.get("taste", {}),
            curated=state.get("curated", {}),
            cards=state.get("cards", {}),
        )
        # Flag that critic has run once.
        return {"critic_feedback": critic_json, "critic_ran": True}

    def n_controller(state: WatchState) -> WatchState:
        ctl = controller(logger, llm, dict(state))
        action = ctl.get("action", "accept")

        # only one revise after critic
        revision_done = state.get("revision_done", False)
        if revision_done and action in ("revise_candidates", "revise_curation"):
            action = "accept"

        # If controller requests a revision, mark it + increment iterations
        next_iters = state.get("iterations", 0) or 0
        if action in ("revise_candidates", "revise_curation"):
            revision_done = True
            next_iters += 1

        return {
            "controller_action": action,
            "controller_rationale": ctl.get("rationale"),
            "answer": ctl.get("message_to_user"),
            "iterations": next_iters,
            "revision_done": revision_done,
        }

    #Route after explain to either critic (only once) or controller 
    def route_after_explain(state: WatchState) -> str:
        # Critic runs ONLY once
        if state.get("critic_ran", False):
            return "controller"
        return "critic"

    #  Updated controller routing 
    def route_controller(state: WatchState) -> str:
        action = state.get("controller_action", "accept")
        iters = state.get("iterations", 0) or 0
        max_iters = state.get("max_iters", 2) or 2

        if action == "answer_question":
            return END

        if iters >= max_iters:
            return END

        if action == "revise_candidates":
            return "candidates"

        if action == "revise_curation":
            return "curate"

        return END

    g = StateGraph(WatchState)
    g.add_node("research", n_research)
    g.add_node("fingerprint", n_fingerprint)
    g.add_node("taste", n_taste)
    g.add_node("candidates", n_candidates)
    g.add_node("curate", n_curate)
    g.add_node("explain", n_explain)
    g.add_node("critic", n_critic)
    g.add_node("controller", n_controller)

    g.set_entry_point("research")
    g.add_edge("research", "fingerprint")
    g.add_edge("fingerprint", "taste")
    g.add_edge("taste", "candidates")
    g.add_edge("candidates", "curate")
    g.add_edge("curate", "explain")

    # Instead of always going to critic, go to critic once, otherwise controller
    g.add_conditional_edges("explain", route_after_explain, {
        "critic": "critic",
        "controller": "controller",
    })

    g.add_edge("critic", "controller")

    # Controller decides what to do next
    g.add_conditional_edges("controller", route_controller, {
        "candidates": "candidates",
        "curate": "curate",
        END: END
    })

    return g.compile(), llm
