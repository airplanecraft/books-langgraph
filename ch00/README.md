# Chapter 0: Foundations

Code for chapter 0. Run every script from the top folder of the repository, for example `OFFLINE=1 python ch00/one_round.py`. Three scripts call a model (`hello_model.py`, `first_tool.py`, `one_round.py`) and replay from `replay/ch00/` with `OFFLINE=1`; the others need no key and no network.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `common.py` (top folder) | 0.1, 0.7, 0.8 | `get_model()`; `say` and `ask_for`; `ScriptedModel` | used by the scripts |
| `hello_model.py` | 0.2 | Send one message, print the reply | `OFFLINE=1 python ch00/hello_model.py` |
| `message_ids.py` | 0.3 | Message objects, their types and ids | `python ch00/message_ids.py` |
| `first_tool.py` | 0.4, 0.5 | What the model sees of a tool; the tool call in a reply | `OFFLINE=1 python ch00/first_tool.py` |
| `one_round.py` | 0.6 | One round by hand, then the answering call | `OFFLINE=1 python ch00/one_round.py` |
| `stand_in.py` | 0.9 | The same example with the stand-in model | `python ch00/stand_in.py` |
| `quiz_ids.py`, `quiz_no_tool.py`, `quiz_two_rounds.py` | self-check | Runs behind the predict questions | `python ch00/quiz_ids.py` |

Key output of `one_round.py`: `tool returned: delayed: waiting for stock`

Exercises are in the book. Reference solutions: `solutions/ch00_ex1.py`, `solutions/ch00_ex2.py`, `solutions/ch00_ex3.py`. Tests: `tests/test_ch00.py`.
