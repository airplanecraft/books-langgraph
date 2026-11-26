# Chapter 13: Project, an email workflow

Code for chapter 13. Run every script from the top folder of the repository, for example `python ch13/step1_loop.py`. Only `workflow.py` calls the real model (four times), and `OFFLINE=1 python ch13/workflow.py` replays it. The other scripts use the stand-in model or no model, and need no key and no network. The mail service is a dictionary, and nothing leaves your computer. The retry waits are 0.01 seconds, with no jitter.

Each step file holds everything the step needs, so you can run it alone. `workflow.py` is the finished file: the listings of the steps with the real model and one demo run.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `step1_loop.py` | 13.1, 13.2, 13.3 | State, tool, `classify`, the agent loop, `to_person`, with the stand-in | `python ch13/step1_loop.py` |
| `step2_approve.py` | 13.4, 13.5 | `approve` with `interrupt`, `send`, a checkpointer, `run_ticket` | `python ch13/step2_approve.py` |
| `step3_fail.py` | 13.6 | A failing send without a retry policy | `python ch13/step3_fail.py` |
| `step4_errors.py` | 13.7, 13.8 | A retry policy and an error handler on `send` | `python ch13/step4_errors.py` |
| `step5_replay.py` | 13.9 | Reject, go back to the copy before the first model call, run again | `python ch13/step5_replay.py` |
| `workflow.py` | 13.10, 13.11 | The finished workflow with the real model | `OFFLINE=1 python ch13/workflow.py` |
| `optional_parallel.py` | 13.12 | Two lookups in one super-step (chapter 10) | `python ch13/optional_parallel.py` |
| `optional_memory.py` | 13.13 | A preference kept in the store across tickets (chapter 12) | `python ch13/optional_memory.py` |
| `pitfall_thread.py` | 13.14 | Two tickets on one thread id | `python ch13/pitfall_thread.py` |
| `pitfall_replay.py` | 13.15 | A replay after the send sends again | `python ch13/pitfall_replay.py` |
| `quiz_refund.py`, `quiz_replay_tools.py`, `quiz_fallback.py` | self-check | Runs behind the predict questions | `python ch13/quiz_refund.py` |

Key output of `workflow.py`: `sent | calls: 2 | mails: 1`

Exercises are in the book. Reference solutions: `solutions/ch13_ex1.py`, `solutions/ch13_ex2.py`, `solutions/ch13_ex3.py`. Tests: `tests/test_ch13.py` and `tests/test_ch13_more.py`.
