# Chapter 3: Branching and loops

Code for chapter 3. Run every script from the top folder of the repository, for example `python ch03/route.py`. Only `route_model.py` calls a model, and `OFFLINE=1 python ch03/route_model.py` replays it; the others need no key and no network.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `route.py` | 3.1 | State, `classify` and a routing function | `python ch03/route.py` |
| `route.py` | 3.2 | Reply nodes and the conditional edge | `python ch03/route.py` |
| `route.py` | 3.3 | The graph run on two emails, and its conditional edges | `python ch03/route.py` |
| `route_model.py` | 3.4 | The model classifies, the routing function reads the result | `OFFLINE=1 python ch03/route_model.py` |
| `loop.py` | 3.5 | Draft and review nodes, with a note that changes between tries | `python ch03/loop.py` |
| `loop.py` | 3.6 | The loop graph, built and run | `python ch03/loop.py` |
| `steps.py` | 3.7 | Each node run is one super-step; a node reads its number | `python ch03/steps.py` |
| `limit.py` | 3.8 | A loop that never passes stops at the recursion limit | `python ch03/limit.py` |
| `limit_edge.py` | 3.9 | Three node runs: limit 3 raises after them, limit 4 finishes | `python ch03/limit_edge.py` |
| `command_goto.py` | 3.10 | A node returns a `Command` with `update` and `goto` | `python ch03/command_goto.py` |
| `command_goto.py` | 3.11 | The graph for that node, and its drawn edges | `python ch03/command_goto.py` |
| `command_reducer.py` | 3.12 | The update of a `Command` goes through a reducer | `python ch03/command_reducer.py` |
| `pitfall_draw.py` | 3.13 | A routing function without a return type: no conditional edges | `python ch03/pitfall_draw.py` |
| `pitfall_command.py` | 3.14 | A `Command` without a return type: edges are not drawn | `python ch03/pitfall_command.py` |
| `pitfall_name.py` | 3.15 | A misspelled node name in three places | `python ch03/pitfall_name.py` |
| `pitfall_both.py` | 3.16 | A `Command` plus a plain edge from the same node | `python ch03/pitfall_both.py` |
| `quiz_route.py`, `quiz_steps.py`, `quiz_limit.py`, `quiz_command.py`, `quiz_name.py` | self-check | Runs behind the predict questions | `python ch03/quiz_route.py` |
| `limit_default.py` | section 3.4 | The default limit: 10,006 node runs finish, 10,007 raise (output not printed in the book) | `python ch03/limit_default.py` |

Key output of `limit_edge.py`: `GraphRecursionError` after three runs at limit 3, and `finished` at limit 4.

Exercises are in the book. Reference solutions: `solutions/ch03_ex1.py`, `solutions/ch03_ex2.py`, `solutions/ch03_ex3.py`. Tests: `tests/test_ch03.py` and `tests/test_ch03_more.py`.
