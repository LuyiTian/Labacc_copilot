# Wet-Lab Omics Copilot — **Finalized MVP plan (v1)**

Version: v1

## What changed vs last draft

* **ImageReader** → use a *multimodal LLM API* via LangChain’s native image-input support (no custom CV stack in MVP). ([Langchain Python][1])
* **Web search** → assume you already have a **DeepResearch** tool; we’ll expose it as a single LangChain tool and skip building a crawler.
* **Multi-turn chat** → design around **persistent, resumable conversations** with short- and long-term memory in **LangGraph** (checkpointer). ([LangChain AI][2], [LangChain Blog][3])
* **UI** → recommend **Chainlit** for a simple, local, chat-first web UI (file uploads, intranet-friendly), with **Gradio** as backup; both are easy to self-host. ([docs.chainlit.io][4], [gradio.app][5])

---

## High-level architecture (MVP)

### Agents (LangGraph nodes)

* **Planner**: reads project/experiment `README.md` (YAML front matter + narrative) → clarifies goal for this round.
* **Retriever**: (a) project RAG over `/ref` + `/todo_history`, (b) optional call to your **DeepResearch** tool for external literature (returns snippet+URL).
* **Analyst**: parses CSV/XLSX with `pandas/openpyxl`; ingests images via **multimodal LLM** (e.g., GPT-4o, Gemini, Claude Sonnet vision) through LangChain’s image message content; computes simple QC/summary. ([Langchain Python][1])
* **Critic**: ranks likely failure modes; proposes ≤2 controlled changes; optional small **screening DOE** scaffold.
* **Writer**: emits a **DecisionCard** (Pydantic) + Markdown; saves to `/todo_history/`; includes inline citations (local or DeepResearch URLs).

### Memory & sessions

* **Short-term**: conversation state as part of the graph state (multi-turn).
* **Long-term**: append DecisionCards & session summaries to `/todo_history` and index them; retrieve for future rounds.
* **Persistence**: **SQLite checkpointer** (local, robust on intranet) to resume threads and approve gated steps (HITL). ([LangChain Blog][3], [LangChain AI][6])
* **Per-user threads**: `thread_id = f"{user_id}:{session_uuid}"` to namespace histories and prevent cross-user leakage.

---

## Modules & contracts (what your coding agent should implement)

### 1) Project & experiment loaders

* Parse `README.md` front matter with `python-frontmatter`; keep the free-text body.
* Normalize experiment tables (CSV/XLSX) with `pandas/openpyxl`.
* Collect image paths (`.png`) for **multimodal** prompts.

### 2) Retrieval (local only in MVP)

* Index `/ref` and `/todo_history` (PDF/MD/TXT) with Unstructured→chunks→embeddings (e.g., `e5-large-v2`) + Chroma/FAISS; add cross-encoder rerank & contextual compression before prompting. ([Langchain Python][1], [gradio.app][5])
* Return: `{text, source_path}` snippets.

### 3) External research tool (your DeepResearch)

* Expose as a LangChain Tool: `deep_research(query) -> list[{title, url, snippet}]`.
* Implementation note: under the hood, call a function API to run the deep-research graph and extract citations into `{title,url,snippet}` entries.
* Writer cites URLs from this tool; no internal web pipeline required.

### 3.1) Folder/file visualization & management (server-side)

* Scope all file operations to a per-user project root.
* List directories and files with basic metadata (size, mtime); provide actions: open (preview or download), rename/move, delete.
* Guardrails: normalize all paths, deny traversal outside root, optionally deny following symlinks that resolve outside root, log mutations to `/data/history/`.

### 4) Multimodal **ImageReader** (no CV stack)

* Use LangChain’s **multimodal message content**: pass images (bytes/paths) inside chat messages to the chosen provider. Examples & patterns: *“how to pass multimodal data to models”* and *“multimodal prompts”* in LangChain docs. ([Langchain Python][1])
* For OpenAI-style vision endpoints, follow provider’s image guide (PNG/JPEG in message content). ([OpenAI Platform][7])
* Output: concise caption or structured key observations (e.g., “gel lane 3 no band; smear at \~200bp”).

### 5) Heuristics & proposals

* Generic checks (controls present? incubation/timeouts? reagent lot issues? instrument drift?).
* **Change budget**: ≤2 factors per round; require controls for risky changes.
* Optional **DOE screening** (2–3 factors × 2 levels) as next-round scaffold.

### 6) DecisionCard (Pydantic)

```python
class Finding(BaseModel):
    statement: str
    evidence: list[str]      # file paths or URLs
    confidence: Literal["low","medium","high"]

class ProposedChange(BaseModel):
    factor: str
    current: str | float | None
    proposal: str | float
    rationale: str
    risk: str
    expected_effect: str

class NextRoundDesign(BaseModel):
    design_type: Literal["screening","fractional","lhs"]
    factors: dict[str, list[str|float]]
    runs: int
    notes: str

class DecisionCard(BaseModel):
    project_id: str
    experiment_id: str
    summary: str
    key_findings: list[Finding]
    proposed_changes: list[ProposedChange]
    next_design: NextRoundDesign | None
    references: list[str]    # paths or URLs
```

---

## Conversational flow (multi-turn, resumable)

1. **User** uploads/points to an experiment folder → asks “why low yield?”
2. **Planner** extracts goals/metrics from experiment README → sets analysis plan.
3. **Retriever** fetches relevant `/ref` and earlier DecisionCards; calls **DeepResearch** if asked for new literature.
4. **Analyst**:

   * Tables: compute deltas vs. expected; generate small plots/tables (if asked).
   * Images: send to **multimodal LLM** via LangChain image content; get captions/observations. ([Langchain Python][1])
5. **Critic** consolidates causes; proposes ≤2 changes with rationale/risks; suggests a minimal screening design if needed.
6. **Writer** drafts the DecisionCard; **HITL approval**; then persists to `/todo_history/` and updates the index.
7. Next turns: user negotiates parameters (“let’s try 42 °C but shorter time”) → Critic revises → Writer updates DecisionCard.

**Memory implementation notes**

* Add **short-term memory** in LangGraph state for multi-turn chat; **long-term** via `/todo_history` + index. See LangGraph’s “add memory” how-to and persistence docs. ([LangChain AI][2])

---

## UI: simple, local, intranet-friendly

**Recommended:** **Chainlit**

* Purpose-built chat UI; pip-install; trivial to deploy on your intranet server; supports file uploads, session state, subpath deploy (`--root-path`). ([docs.chainlit.io][4])
* Many tutorials show end-to-end chat apps with LangChain/LangGraph. ([DataCamp][8])

### Deployment & auth (v1, Option B)

* Single Chainlit instance behind Nginx with Basic Auth (few users, simple ops):
  - Nginx `auth_basic` with `htpasswd`; Nginx forwards authenticated username as `$remote_user` header to Chainlit.
  - App maintains a static mapping `{username -> project_root}` and restricts all file ops under that root.
  - Persist LangGraph state with `thread_id = f"{username}:{session_uuid}"`.
* Upgrade path: swap Basic Auth for OAuth2/OpenID via OAuth2-Proxy/Authentik/Keycloak without changing app logic.

**Alternative:** **Gradio ChatInterface**

* One-file app; pass `multimodal=True` to accept images/files in chat; easy local hosting. ([gradio.app][5])

**Folder selection**

* Keep it simple: a text field for **project root path** + backend lists experiments to populate a dropdown; no need for a graphical file explorer in MVP.

---

## Key code patterns your coding agent will need (pseudocode)

### A) LangChain multimodal prompt (image in message)

```python
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI  # or other provider with vision

msg = HumanMessage(content=[
    {"type": "text", "text": "Summarize key observations from this gel image."},
    {"type": "image_url", "image_url": f"file://{path_to_png}"}  # or bytes
])
resp = vision_llm.invoke([msg])  # returns text observations
```

(Adapt provider-specific variants per LangChain’s **multimodal inputs** & **prompts** guides.) ([Langchain Python][1])

### B) LangGraph state & checkpointer (multi-turn)

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.sqlite import SqliteSaver  # or Postgres
checkpointer = SqliteSaver("copilot.sqlite")

graph = StateGraph(State)  # add planner, retriever, analyst, critic, writer
# ... add nodes & edges ...
app = graph.compile(checkpointer=checkpointer)
# route chat turns by thread_id to persist multi-turn context, namespaced per user
# thread_id = f"{username}:{uuid4()}"
```

([LangChain Blog][3], [LangChain AI][6])

### C) Gradio/Chainlit chat wiring (minimal)

* **Chainlit**: define an async handler that forwards `(message, thread_id)` into the LangGraph app; attach uploaded file paths from `message.elements`. ([Medium][9])
* **Gradio**: `gr.ChatInterface(fn, multimodal=True)` where `fn(messages, files)` calls the graph and returns a reply. ([gradio.app][5])

---

## Test plan (acceptance)

* **Multi-turn**: keep a 6–10 message dialogue; verify context carry-over after a server restart (SQLite checkpointer). ([LangChain Blog][3])
* **Image understanding**: drop a `*.png` gel/QC plot → receive sensible observations via multimodal LLM. ([Langchain Python][1])
* **DecisionCard**: for two toy experiments, produce plausible root-cause analysis + ≤2 proposed changes + citations; file saved to `/todo_history/` and re-indexed.
* **DeepResearch** tool: when invoked, Writer includes URL citations in the DecisionCard.

---

## Milestones (re-scoped)

1. **UI + sessions (Chainlit)**: project path selector; chat; attach files; thread\_id routing. ([docs.chainlit.io][4])
2. **Loaders**: front matter + experiments (tables/images).
3. **Local RAG**: `/ref` + `/todo_history` with compression+rerank.
4. **Multimodal**: ImageReader via LangChain image content; provider config. ([Langchain Python][1])
5. **Analyst/Critic/Writer**: heuristics + DecisionCard.
6. **DeepResearch tool**: simple tool shim + citation plumbing.
7. **Persistence**: SQLite checkpointer; basic “resume” button.

---

## Notes & options

* If you prefer Streamlit over Chainlit, `st.chat_input` + a sidebar selector also works; Gradio is simpler for multimodal out-of-the-box. ([gradio.app][5])
* For Anthropic/Google/OpenAI vision models, match the **provider-specific** image content schema as per LangChain docs. ([Langchain Python][1])
* If later you need richer image reasoning, you can still keep this abstraction and swap in a CV tool; the agent contract doesn’t change.

If you want, I can turn this into a **task list with code stubs** (Chainlit app, LangGraph graph, tool adapters, and the Pydantic models) so your coding agent can start committing on day one.

[1]: https://python.langchain.com/docs/how_to/multimodal_inputs/?utm_source=chatgpt.com "How to pass multimodal data to models"
[2]: https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/?utm_source=chatgpt.com "Add memory"
[3]: https://blog.langchain.com/langgraph-v0-2/?utm_source=chatgpt.com "LangGraph v0.2: Increased customization with new ..."
[4]: https://docs.chainlit.io/?utm_source=chatgpt.com "Chainlit: Overview"
[5]: https://www.gradio.app/docs/gradio/chatinterface?utm_source=chatgpt.com "ChatInterface"
[6]: https://langchain-ai.github.io/langgraph/concepts/persistence/?utm_source=chatgpt.com "LangGraph persistence"
[7]: https://platform.openai.com/docs/guides/images-vision?utm_source=chatgpt.com "Images and vision - OpenAI API"
[8]: https://www.datacamp.com/tutorial/chainlit?utm_source=chatgpt.com "Chainlit: A Guide With Practical Examples"
[9]: https://medium.com/mitb-for-all/its-2025-take-your-llm-apps-to-the-next-level-with-chainlit-00036c8db1ba?utm_source=chatgpt.com "Take your LLM apps to the next level with Chainlit!"
