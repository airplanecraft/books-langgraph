# Chapter 9: Errors and retries

Code for chapter 9. Run every script from the top folder of the repository, for example `python ch09/fails.py`. No script calls a model, and none needs a key, a network or a database: the failures come from a toy mail server that the scripts switch off on purpose, and the checkpointer is `InMemorySaver`. Nothing waits long: the scripts use a wait of 0.01 seconds, and `backoff.py` records the waits instead of sleeping.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `fails.py` | 9.1, 9.2 | A node raises: the run stops and nothing is kept | `python ch09/fails.py` |
| `node_error.py` | 9.3 | What the checkpointer holds after the failed run: values, `next`, task error | `python ch09/node_error.py` |
| `resume_after_error.py` | 9.4 | `invoke(None, config)` runs the failed node again and carries on | `python ch09/resume_after_error.py` |
| `retry.py` | 9.5, 9.6 | A retry policy and a mail server that fails twice, then five times | `python ch09/retry.py` |
| `retry_on.py` | 9.7 | Which exceptions are retried, and what `retry_on` replaces | `python ch09/retry_on.py` |
| `backoff.py` | 9.8 | The waits a policy asks for, recorded instead of slept | `python ch09/backoff.py` |
| `error_handler.py` | 9.9 | An error handler after the retries run out | `python ch09/error_handler.py` |
| `durability.py` | 9.10, 9.11 | Copies left under each durability mode, with the server up and down | `python ch09/durability.py` |
| `durability_order.py` | 9.12 | When the checkpointer is asked to save, under `"sync"` and `"exit"` | `python ch09/durability_order.py` |
| `pitfall_twice.py` | 9.13 | A retry sends the mail twice, unless a key names it | `python ch09/pitfall_twice.py` |
| `pitfall_none.py` | 9.14 | `invoke(None)` on a new thread and on a finished thread | `python ch09/pitfall_none.py` |
| `pitfall_handler.py` | 9.15 | An error handler without `goto`, and one with a wrongly named parameter | `python ch09/pitfall_handler.py` |
| `quiz_attempts.py`, `quiz_handler.py`, `quiz_copies.py` | self-check | Runs behind the predict questions | `python ch09/quiz_attempts.py` |

Key output of `retry.py`: `attempts: 3`

Exercises are in the book. Reference solutions: `solutions/ch09_ex1.py`, `solutions/ch09_ex2.py`, `solutions/ch09_ex3.py`. Tests: `tests/test_ch09.py`, `tests/test_ch09_solutions.py` and `tests/test_ch09_more.py`.
