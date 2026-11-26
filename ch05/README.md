# Chapter 5: Persistence

Code for chapter 5. Run every script from the top folder of the repository, for example `python ch05/get_state.py`. Only `threads.py` calls a model, and `OFFLINE=1 python ch05/threads.py` replays it; the others use the stand-in model of chapter 0 or no model, and need no key and no network. No script needs a database: the checkpointer is `InMemorySaver`.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `no_memory.py` | 5.1 | Two invokes of the agent graph of chapter 4: the second knows nothing of the first | `python ch05/no_memory.py` |
| `threads.py` | 5.2, 5.3 | A chat graph with a checkpointer and two threads | `OFFLINE=1 python ch05/threads.py` |
| `get_state.py` | 5.4 | The checkpoints of one run | `python ch05/get_state.py` |
| `snapshot.py` | 5.5 | The state snapshot of the newest checkpoint | `python ch05/snapshot.py` |
| `merge_input.py` | 5.6 | A second invoke on the same thread: input merged, graph runs again | `python ch05/merge_input.py` |
| `no_thread.py` | 5.8 | A call without a thread id | `python ch05/no_thread.py` |
| `no_saver.py` | 5.9 | A thread id on a graph without a checkpointer | `python ch05/no_saver.py` |
| `lost_on_exit.py` | 5.7 | A second program finds no copies of the first | `python ch05/lost_on_exit.py` |
| `quiz_count.py`, `quiz_threads.py`, `quiz_merge.py` | self-check | Runs behind the predict questions | `python ch05/quiz_count.py` |

Key output of `snapshot.py`: `metadata: {'source': 'loop', 'step': 2, 'parents': {}}`

Exercises are in the book. Reference solutions: `solutions/ch05_ex1.py`, `solutions/ch05_ex2.py`, `solutions/ch05_ex3.py`. Tests: `tests/test_ch05.py`, `tests/test_ch05_more.py` and `tests/test_ch05_errors.py`.
