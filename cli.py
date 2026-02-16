import typer
from rich import print as rprint
from rich.console import Console

from next_watch_ai.config import load_settings
from next_watch_ai.logging_utils import setup_logging
from agents.input_agent import normalize_content_type
from agents.controller_agent import controller
from pipeline import run_pipeline
from graph import build_graph
app = typer.Typer(add_completion=False)
console = Console()

def prompt_seeds() -> list[str]:
    console.print("\nEnter 5 titles (one per line). Press Enter after each:")
    seeds = []
    while len(seeds) < 5:
        s = typer.prompt(f"Title {len(seeds)+1}").strip()
        if s:
            seeds.append(s)
    return seeds

@app.command()
def run():
    settings = load_settings()
    logger = setup_logging(settings.log_level)

    ct_raw = typer.prompt("Are you inputting movies, TV shows, or both? (movie/tv/both)", default="both")
    content_type = normalize_content_type(ct_raw)

    seed_titles = prompt_seeds()

    extra_specs = typer.prompt(
        "Any other specs? (1–2 sentences, optional)",
        default="",
        show_default=False,
    ).strip()

    logger.info(f"[CLI] content_type={content_type} seeds={seed_titles} extra_specs={extra_specs}")

    graph, llm = build_graph(logger, settings)  

    #################################
    compiled_graph, llm = build_graph(logger, settings)

    png_bytes = compiled_graph.get_graph().draw_mermaid_png()
    with open("next-watch-ai-workflow.png", "wb") as f:
        f.write(png_bytes)

    print("Saved: next-watch-ai-workflow.png")

    #################################
    state = {
        "content_type": content_type,
        "seed_titles": seed_titles,
        "extra_specs": extra_specs,
        "iterations": 0,
        "max_iters": 2,
    }

    # Run full pipeline once
    result = graph.invoke(state)

    # --- print cards as you already do ---
    taste = result.get("taste", {})
    cards = (result.get("cards", {}) or {}).get("cards", [])

    rprint("\n[bold]YOUR TASTE (film-student summary)[/bold]")
    rprint(taste.get("taste_summary", ""))

    core = taste.get("core_signals", []) or []
    if core:
        rprint("\n[bold]Core signals:[/bold]")
        for s in core[:8]:
            rprint(f" • {s}")

    rprint("\n[bold]RECOMMENDATIONS (spoiler-free)[/bold]")
    for i, c in enumerate(cards, start=1):
        title = c.get("title", "")
        year = c.get("year")
        header = f"{i}. {title}" + (f" ({year})" if year else "")
        rprint(f"\n[bold]{header}[/bold]")
        for b in (c.get("why_this_fits", []) or [])[:3]:
            rprint(f" • {b}")
        wf = (c.get("watch_for", "") or "").strip()
        if wf:
            rprint(f"[dim]Watch for:[/dim] {wf}")

    # Follow-up Q&A 
    while True:
        q = typer.prompt("\nAsk a question about these recs (or type 'exit')", default="exit")
        if q.strip().lower() in ["exit", "quit", "q"]:
            break

        state_for_qa = dict(result)
        state_for_qa["user_question"] = q

        ctl = controller(logger, llm, state_for_qa)  
        answer = ctl.get("message_to_user", "")

        rprint(f"\n[bold]Answer:[/bold]\n{answer}")
        action = ctl.get("action", "answer_question")
        if action in ("revise_candidates", "revise_curation"):
            #  restart a clean pipeline using only the true inputs + (optionally) updated extra_specs
            new_state = {
                "content_type": result["content_type"],
                "seed_titles": result["seed_titles"],
                "extra_specs": result.get("extra_specs", ""),
                "iterations": 0,
                "max_iters": state["max_iters"],
            }
            result = graph.invoke(new_state)
    rprint("\n[dim]Logs are saved in ./logs/[/dim]")
    

if __name__ == "__main__":
    app()
