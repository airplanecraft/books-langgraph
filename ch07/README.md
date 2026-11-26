# Chapter 7: Asking before acting

Code for chapter 7. Run every script from the top folder of the repository, for example `python ch07/pause.py`. Only `approve.py` calls a model, and `OFFLINE=1 python ch07/approve.py` replays it; the others use the stand-in model of chapter 0 or no model, and need no key and no network. Every graph here is compiled with `InMemorySaver`, except in `no_checkpointer.py`, where the missing checkpointer is the point.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `no_question.py` | 7.1 | The agent loop of chapter 4 with a refund tool that nobody asks about | `python ch07/no_question.py` |
| `pause.py` | 7.2 | A node calls `interrupt`: `invoke` returns `__interrupt__`, and the snapshot is paused at the node | `python ch07/pause.py` |
| `resume.py` | 7.3 | `Command(resume=...)` on the same thread: the reply is the value of `interrupt` | `python ch07/resume.py` |
| `pitfall_rerun.py` | 7.4 | The node starts again: a draft made before `interrupt` is made twice | `python ch07/pitfall_rerun.py` |
| `fix_rerun.py` | 7.5 | The fix: the model call gets a node of its own | `python ch07/fix_rerun.py` |
| `approve.py` | 7.6, 7.7 | A drafted reply, a question to a person, then send | `OFFLINE=1 python ch07/approve.py` |
| `edit_reject.py` | 7.8 | One review node with three replies: approve, edit, reject | `python ch07/edit_reject.py` |
| `ask_in_tool.py` | 7.9, 7.10 | The refund tool asks the question itself | `python ch07/ask_in_tool.py` |
| `two_tools.py` | 7.11 | One reply with two tools: a resume starts both again | `python ch07/two_tools.py` |
| `two_questions.py` | 7.12 | Two interrupts in one node: resume values are matched in order | `python ch07/two_questions.py` |
| `no_checkpointer.py` | 7.13 | No checkpointer: the pause works, the resume raises `RuntimeError` | `python ch07/no_checkpointer.py` |
| `pitfall_resume.py` | 7.14 | Plain input on a paused thread, and a resume on the wrong thread | `python ch07/pitfall_resume.py` |
| `pitfall_except.py` | 7.15 | A bare `except` around `interrupt` swallows the pause | `python ch07/pitfall_except.py` |
| `quiz_next.py`, `quiz_value.py`, `quiz_prepare.py`, `quiz_two.py` | self-check | Runs behind the predict questions | `python ch07/quiz_value.py` |

Key output of `resume.py`: `review got: approved`

Exercises are in the book. Reference solutions: `solutions/ch07_ex1.py`, `solutions/ch07_ex2.py`, `solutions/ch07_ex3.py`. Tests: `tests/test_ch07.py`, `tests/test_ch07_more.py` and `tests/test_ch07_solutions.py`.
