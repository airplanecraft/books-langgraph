# Chapter 11: Subgraphs and several agents

Code for chapter 11. Run every script from the top folder of the repository, for example `python ch11/subgraph_shared.py`. Only `handoff_real.py` calls a model, and `OFFLINE=1 python ch11/handoff_real.py` replays it; the others use the stand-in model of chapter 0 or no model, and need no key and no network.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `subgraph_shared.py` | 11.1 | A lookup graph with its own state, run alone | `python ch11/subgraph_shared.py` |
| `subgraph_shared.py` | 11.2 | The lookup graph added as a node: shared keys go in and come back, the private key is dropped | `python ch11/subgraph_shared.py` |
| `pitfall_duplicate.py` | 11.3 | A shared key with `operator.add` is added twice; `add_messages` is not | `python ch11/pitfall_duplicate.py` |
| `subgraph_transform.py` | 11.4 | A node calls the subgraph with `invoke` and returns only what is new | `python ch11/subgraph_transform.py` |
| `subgraph_memory.py` | 11.5 | `checkpointer` set to `None`, `True` and `False` on the subgraph | `python ch11/subgraph_memory.py` |
| `subgraph_interrupt.py` | 11.6 | `interrupt` inside a subgraph, then the resume | `python ch11/subgraph_interrupt.py` |
| `subgraph_rerun.py` | 11.7 | A parent node that calls the subgraph starts again on a resume | `python ch11/subgraph_rerun.py` |
| `handoff_basic.py` | 11.8 | The smallest handoff: no model, no tools | `python ch11/handoff_basic.py` |
| `handoff.py` | 11.9 | A helper that builds an agent loop as a subgraph | `python ch11/handoff.py` |
| `handoff.py` | 11.10 | The tools, with a handoff tool that returns a Command for the parent | `python ch11/handoff.py` |
| `handoff.py` | 11.11 | Two agents in a parent graph; support hands over to billing | `python ch11/handoff.py` |
| `handoff_update.py` | 11.12 | Three versions of the handoff update and what billing reads | `python ch11/handoff_update.py` |
| `handoff_real.py` | 11.13 | The two agents with the real model | `OFFLINE=1 python ch11/handoff_real.py` |
| `handoff_pitfalls.py` | 11.14 | No destinations, an extra edge, a `Literal` type, a subgraph run alone | `python ch11/handoff_pitfalls.py` |
| `handoff_two_calls.py` | 11.15 | A handoff in a reply with a second tool call: billing reads an open request | `python ch11/handoff_two_calls.py` |
| `quiz_double.py`, `quiz_memory.py`, `quiz_rerun.py`, `quiz_handoff.py` | self-check | Runs behind the predict questions | `python ch11/quiz_double.py` |

Key output of `subgraph_memory.py`: `True visits [1, 2, 1]`

Exercises are in the book. Reference solutions: `solutions/ch11_ex1.py`, `solutions/ch11_ex2.py`, `solutions/ch11_ex3.py`. Tests: `tests/test_ch11.py`.
