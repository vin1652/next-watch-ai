# ===============================
# 🎬 NEXT-WATCH-AI
# Agentic Movie & TV Recommendation System
# ===============================

# --------------------------------
# 🧠 Overview
# --------------------------------
Next-Watch-AI is an agentic recommendation system that generates highly personalized
movie and TV show recommendations using a multi-agent workflow powered by LLMs.

Instead of simple keyword or genre matching, the system:
- Analyzes storytelling style and themes of user input titles
- Builds a deep "taste profile"
- Generates and critiques recommendations
- Iteratively improves them using an agent controller
- Allows conversational Q&A about recommendations

This project demonstrates how to build a structured multi-agent LLM system using:
- LangGraph (agent orchestration)
- Groq LLM API
- CLI interface
- Persistent conversational state
- Logging + observability

It is designed as a **portfolio-grade agentic AI system** that mirrors real-world
multi-agent orchestration patterns used in production AI systems.

# --------------------------------
# 🚀 Key Features
# --------------------------------
✔ Agentic workflow using LangGraph  
✔ Multi-step reasoning pipeline  
✔ Taste fingerprinting from seed titles  
✔ Candidate generation + curation loop  
✔ Critic agent for quality control  
✔ Controller agent that decides next actions  
✔ Conversational Q&A about recommendations  
✔ CLI interface  
✔ Structured logging for debugging  
✔ Graph visualization support  

# --------------------------------
# 🧱 System Architecture
# --------------------------------
The system uses multiple specialized agents connected through LangGraph.

User Input → Agent Pipeline → Recommendations → Q&A Controller

Main agents:

1. Research Agent
   Scrapes and gathers information about input movies/TV shows.

2. Fingerprint Agent
   Extracts storytelling DNA:
   - themes
   - tone
   - pacing
   - narrative structure
   - style signals

3. Taste Agent
   Builds a unified taste profile from all fingerprints.

4. Candidate Agent
   Generates a large pool of matching movies/shows using the taste profile.

5. Curator Agent
   Selects the best final recommendations from the candidate pool.

6. Explanation Agent
   Writes spoiler-free recommendation cards.

7. Critic Agent
   Evaluates recommendations against constraints and quality.

8. Controller Agent (brain)
   Decides whether to:
   - accept results
   - revise candidates
   - revise curation
   - answer user questions

This creates a **true agentic loop**, not just a linear pipeline.

# --------------------------------
# 🔁 Agentic Workflow Logic
# --------------------------------

FULL PIPELINE RUNS ONCE:
research → fingerprint → taste → candidates → curate → explain → critic → controller

Controller decides:
- accept → finish
- revise_candidates → regenerate pool
- revise_curation → reselect from pool

After recommendations are shown:
- user can ask questions
- controller answers WITHOUT rerunning pipeline
- pipeline only reruns if user requests new recommendations

This creates a conversational recommender system.

# --------------------------------
# 🗂 Project Structure
# --------------------------------
```
next-watch-ai/
│
├── next_watch_ai/
│   ├── agents/
│   │   ├── research_agent.py
│   │   ├── fingerprint_agent.py
│   │   ├── taste_agent.py
│   │   ├── candidate_agent.py
│   │   ├── curator_agent.py
│   │   ├── explanation_agent.py
│   │   ├── critic_agent.py
│   │   └── controller_agent.py
│   │
│   ├── graph/
│   │   └── build_graph.py
│   │
│   ├── llm.py
│   ├── config.py
│   ├── logging_utils.py
│   ├── cli.py
│   ├── graph_state.py
│   └── firecrawl_utils.py
│
├── logs/
├── output/
└── README.md
```
# --------------------------------
# 🖥 CLI Usage
# --------------------------------

Run the app:

python -m next_watch_ai.cli run

You will be prompted:

1. Movie / TV / Both
2. 5 seed titles
3. Optional preferences
   (example: "character driven, not too many main characters")

System will generate recommendations.

Then conversational mode begins:
You can ask:
- "Why did you recommend X?"
- "Which is darkest?"
- "Which has best cinematography?"

Type exit to quit.

# --------------------------------
# 🧠 Example Interaction
# --------------------------------

Input titles:
Aftersun
Manchester by the Sea
Parasite
Columbus
Eraserhead

Extra specs:
"Character driven, few main characters"

System generates:
- Taste profile
- Recommendation cards
- Q&A enabled

User can then ask:
"Which one is the slowest?"
"Which matches Aftersun most?"

Controller agent answers using stored state.

# --------------------------------
# 🔍 Logging & Observability
# --------------------------------

All agent steps are logged:
- research output
- fingerprint extraction
- taste profile
- candidate pool
- curator picks
- critic feedback
- controller decisions

Logs saved in:
./logs/

This allows debugging and transparency into agent decisions.

# --------------------------------
# 🧪 Technologies Used
# --------------------------------

Python  
LangGraph  
Groq LLM API  
Typer CLI  
Rich terminal formatting  
Mermaid graph visualization  

# --------------------------------
# 🧠 Why This Project Matters
# --------------------------------

This project demonstrates:

✔ Agent orchestration with LangGraph  
✔ Multi-step reasoning pipelines  
✔ Controller-based decision systems  
✔ Persistent conversational state  
✔ Structured prompting + JSON extraction  
✔ LLM reliability handling  
✔ Production-style logging  

It mirrors real-world systems used in:
- AI copilots
- research agents
- enterprise recommender systems
- autonomous LLM workflows

# --------------------------------
# 📊 Visualizing the Agent Graph
# --------------------------------

To generate a workflow diagram:

python

from IPython.display import Image, display
compiled_graph, _ = build_graph(logger, settings)
display(Image(compiled_graph.get_graph().draw_mermaid_png()))

This produces a visual graph of the agent workflow.

# --------------------------------
# 🧭 Future Improvements
# --------------------------------

Potential upgrades:
- Streaming responses
- Memory across sessions
- Vector DB for taste memory
- UI (Streamlit or web app)
- Better critic diversity logic
- Faster models
- Deployment to cloud
- Using Search for movie candidates rather than LLM allows for more recent films


