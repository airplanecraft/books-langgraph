# LangGraph, Step by Step: code

Code for the book *LangGraph, Step by Step* (edition 2026-11). Repository: https://github.com/airplanecraft/books-langgraph.git

Needs Python 3.11 (checked with 3.11.9). Check with `python3 --version`; if it prints an older version, install 3.11 and use `python3.11` in place of `python3`. License: MIT.

1. `git clone https://github.com/airplanecraft/books-langgraph.git && cd books-langgraph`
2. `python3 -m venv .venv && source .venv/bin/activate` (Windows: `python -m venv .venv`, then `.venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. `OFFLINE=1 python ch00/hello_model.py`

`OFFLINE=1` replays the saved replies of the real model, so no key is needed. To call the real model, copy `.env.example` to `.env` and add your DeepSeek key. `python -m pytest` runs the examples offline and checks their output.

| Chapter | Folder | What it covers |
|---|---|---|
| 0 | `ch00/` | Chat models, messages, tools and tool calls; one round by hand; the stand-in model |
| 1 | `ch01/` | The first graph: state, nodes, edges, `compile`, `invoke`; drawing the graph; a node that calls a model |
| 2 | `ch02/` | State schema, state update and reducers: `replace`, `operator.add`, your own reducer, `add_messages`, `MessagesState` |
| 3 | `ch03/` | Conditional edges and routing functions, loops, super-steps, the recursion limit, the `Command` object |
| 4 | `ch04/` | An agent built by hand: model node, tool node, routing, `tools_condition`, two tool calls in one reply, a failing tool |
| 5 | `ch05/` | Persistence: `InMemorySaver`, thread ids, checkpoints, state snapshots, continuing a thread |
| 6 | `ch06/` | Streaming: the modes `values`, `updates`, `messages` and `custom`, several modes at once |
| 7 | `ch07/` | Asking before acting: `interrupt`, `Command(resume=...)`, the node that starts again, approve, edit or reject |
| 8 | `ch08/` | Time travel: the state history, checkpoint replay, checkpoint fork with `update_state` |
| 9 | `ch09/` | Errors and retries: a failed run and what it leaves, `RetryPolicy`, error handlers, durability modes |
| 10 | `ch10/` | Parallel branches (advanced): fan-out, fan-in, `defer=True`, `Send` objects, a failing branch |
| 11 | `ch11/` | Subgraphs and handoffs (advanced): shared keys, subgraph memory, `interrupt` in a subgraph, `Command.PARENT` |
| 12 | `ch12/` | Long-term memory and runtime context (advanced): `InMemoryStore`, namespaces, `context_schema` |
| 13 | `ch13/` | The email workflow: classify, an agent loop that looks up the order and drafts, approve, send, with retries and a fallback |

Tag `v2026.11` is edition 2026-11 of the book. Corrections are listed in `ERRATA.md`. To report a mistake, open an issue in this repository.
