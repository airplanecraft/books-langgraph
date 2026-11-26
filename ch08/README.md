# Chapter 8: Time travel

Code for chapter 8. Run every script from the top folder of the repository, for example `python ch08/history.py`. Only `checkpoint_replay.py` calls a model, and `OFFLINE=1 python ch08/checkpoint_replay.py` runs it from a saved recording; the others use the stand-in model of chapter 0 or no model, and need no key and no network. Every graph here is compiled with `InMemorySaver`, so the history is gone when a script ends.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `ticket.py` | 8.1, 8.2 | The email ticket graph: classify, route, draft, send or escalate; one run | `python ch08/ticket.py` |
| `history.py` | 8.3 | `get_state_history`: five copies, newest first, each with its parent | `python ch08/history.py` |
| `checkpoint_replay.py` | 8.4, 8.5 | `invoke(None, config)` from the copy before `draft`: the model is called again | `OFFLINE=1 python ch08/checkpoint_replay.py` |
| `replay_interrupt.py` | 8.6, 8.7 | A run from an older copy asks the interrupt again | `python ch08/replay_interrupt.py` |
| `fork.py` | 8.8 | `update_state` changes the category; the graph takes the other path; an ordinary invoke then goes on from the newest copy | `python ch08/fork.py` |
| `as_node.py` | 8.9 | The same values with three `as_node` settings give different `next` | `python ch08/as_node.py` |
| `write_reply.py` | 8.10 | Write the reply yourself with `as_node="draft"` and carry on at `send` | `python ch08/write_reply.py` |
| `pitfall_reducer.py` | 8.11 | `update_state` on a reducer key adds to the list | `python ch08/pitfall_reducer.py` |
| `pitfall_newest.py` | 8.12 | A run from the newest copy runs nothing and adds a copy | `python ch08/pitfall_newest.py` |
| `quiz_count.py`, `quiz_rerun.py`, `quiz_fork.py` | self-check | Runs behind the predict questions | `python ch08/quiz_count.py` |

Key output of `history.py`: `[True, True, True, True]`

Exercises are in the book. Reference solutions: `solutions/ch08_ex1.py`, `solutions/ch08_ex2.py`, `solutions/ch08_ex3.py`. Tests: `tests/test_ch08.py`, `tests/test_ch08_more.py`, `tests/test_ch08_claims.py` and `tests/test_ch08_solutions.py`.
