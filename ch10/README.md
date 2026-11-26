# Chapter 10: Parallel branches

Code for chapter 10. Run every script from the top folder of the repository, for example `python ch10/parallel.py`. No script calls a model, so none needs a key or `OFFLINE=1`. Every output is deterministic: no script prints from inside parallel nodes.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `sequential.py` | 10.1 | Five nodes in a row: five super-steps | `python ch10/sequential.py` |
| `parallel.py` | 10.2 | Three edges leave `read`: the lookups share super-step 2 | `python ch10/parallel.py` |
| `parallel_limit.py` | 10.3 | Five node runs in three super-steps: limit 3 raises, limit 4 finishes | `python ch10/parallel_limit.py` |
| `pitfall_no_reducer.py` | 10.4 | Different keys work, the same plain key raises `InvalidUpdateError` | `python ch10/pitfall_no_reducer.py` |
| `merge_order.py` | 10.5 | A reducer on the key; in these runs the notes come out in node-name order | `python ch10/merge_order.py` |
| `fan_in.py` | 10.6 | Separate edges, a list edge and `defer=True` on branches of unequal length | `python ch10/fan_in.py` |
| `defer_optional.py` | 10.7 | Separate edges, a list edge and `defer=True` when a branch may be skipped | `python ch10/defer_optional.py` |
| `defer_waits.py` | 10.8 | `defer=True` also waits for a branch that does not lead to the node | `python ch10/defer_waits.py` |
| `send_map.py` | 10.9 | A `Send` object per email, the results gathered by a reducer | `python ch10/send_map.py` |
| `send_map.py` | 10.10 | The same graph on three emails, one email and none | `python ch10/send_map.py` |
| `failed_branch.py` | 10.11 | Two parallel nodes, one raises; the graph has a checkpointer | `python ch10/failed_branch.py` |
| `failed_branch.py` | 10.12 | What the snapshot shows, and what runs again after the fix | `python ch10/failed_branch.py` |
| `pitfall_send.py` | 10.13 | No reducer on the key the `Send` runs write; no list of destinations | `python ch10/pitfall_send.py` |
| `quiz_steps.py`, `quiz_limit.py`, `quiz_total.py`, `quiz_defer.py`, `quiz_waits.py`, `quiz_send.py` | self-check | Runs behind the predict questions | `python ch10/quiz_steps.py` |

Key output of `parallel.py`: `order`, `plan` and `shipping` all print `super-step 2`, and `draft` prints `super-step 3`.

Exercises are in the book. Reference solutions: `solutions/ch10_ex1.py`, `solutions/ch10_ex2.py`, `solutions/ch10_ex3.py`. Tests: `tests/test_ch10.py` and `tests/test_ch10_more.py`.
