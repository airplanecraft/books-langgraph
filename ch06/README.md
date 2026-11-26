# Chapter 6: Streaming

Code for chapter 6. Run every script from the top folder of the repository, for example `python ch06/modes.py`. Only `tokens.py` and `progress.py` call the real model, and `OFFLINE=1 python ch06/tokens.py` replays them from the recorded chunks; the others use the stand-in model of chapter 0 or no model, and need no key and no network. The scripts that use the tool wait one second inside it on purpose.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `wait.py` | 6.1, 6.2, 6.3 | The agent loop with a slow tool: `invoke` waits, `stream` hands over each node's update | `python ch06/wait.py` |
| `modes.py` | 6.4 | The modes `values` and `updates`, and the default | `python ch06/modes.py` |
| `quiet.py` | 6.5 | Nodes that return `None` or `{}`: `updates` reports them, `values` does not | `python ch06/quiet.py` |
| `messages.py` | 6.6 | The mode `messages` with a stand-in: whole messages, node name and super-step | `python ch06/messages.py` |
| `tokens.py` | 6.7 | The mode `messages` with the real model: the text of each chunk, and the chunks added together | `OFFLINE=1 python ch06/tokens.py` |
| `custom.py` | 6.8, 6.9 | `get_stream_writer()` in a node; `invoke`, `custom` and `updates` compared | `python ch06/custom.py` |
| `together.py` | 6.10 | Two modes at once: `(mode, data)` pairs | `python ch06/together.py` |
| `progress.py` | 6.11, 6.12 | A note from a tool and the reply as it is written, in the terminal | `OFFLINE=1 python ch06/progress.py` |
| `pitfall_shape.py` | 6.13 | A list of one mode gives tuples | `python ch06/pitfall_shape.py` |
| `pitfall_outside.py` | 6.14 | The stream writer outside a run | `python ch06/pitfall_outside.py` |
| `pitfall_early.py` | 6.15 | Leaving the loop early stops the run | `python ch06/pitfall_early.py` |
| `quiz_values.py`, `quiz_modes.py`, `quiz_messages.py` | self-check | Runs behind the predict questions | `python ch06/quiz_values.py` |

Key output of `modes.py`: `default: [['model'], ['tools'], ['model']]`

Exercises are in the book. Reference solutions: `solutions/ch06_ex1.py`, `solutions/ch06_ex2.py`, `solutions/ch06_ex3.py`. Tests: `tests/test_ch06.py` and `tests/test_ch06_more.py`.
