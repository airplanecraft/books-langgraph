# Chapter 12: Long-term memory and runtime context

Code for chapter 12. Run every script from the top folder of the repository, for example `python ch12/share.py`. Only `remember.py` calls a model, and `OFFLINE=1 python ch12/remember.py` replays it; the others use no model and need no key and no network. No script needs a database or an embedding model: the store is `InMemoryStore`, the checkpointer is `InMemorySaver`.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `forget.py` | 12.1 | Two threads: the second does not know what the first was told | `python ch12/forget.py` |
| `store_basics.py` | 12.2 | `put`, `get` and a miss on a store without a graph | `python ch12/store_basics.py` |
| `share.py` | 12.3, 12.4 | A node saves a preference in the store; other threads read it | `python ch12/share.py` |
| `namespaces.py` | 12.5 | Namespaces, prefix search, a filter, a bare string, the limit | `python ch12/namespaces.py` |
| `remember.py` | 12.6, 12.7 | The real model is asked in the style that the store holds | `OFFLINE=1 python ch12/remember.py` |
| `context_state.py` | 12.8 | A user id in the state is saved with the thread | `python ch12/context_state.py` |
| `context.py` | 12.9 | `context_schema=` and `context=`; the context is not in the state | `python ch12/context.py` |
| `context_frozen.py` | 12.10 | A frozen context: a node cannot change it | `python ch12/context_frozen.py` |
| `where.py` | 12.11, 12.12 | State, context and store side by side over three calls | `python ch12/where.py` |
| `pitfall_query.py` | 12.13 | `query=` on a store without an index ranks nothing | `python ch12/pitfall_query.py` |
| `pitfall_missing.py` | 12.14, 12.15 | A call without context, and a graph without a store | `python ch12/pitfall_missing.py` |
| `quiz_prefix.py`, `quiz_counter.py`, `quiz_context.py` | self-check | Runs behind the predict questions | `python ch12/quiz_prefix.py` |

Key output of `where.py`: `tuesday ['visit 3'] | store count: 3`

Exercises are in the book. Reference solutions: `solutions/ch12_ex1.py`, `solutions/ch12_ex2.py`, `solutions/ch12_ex3.py`. Tests: `tests/test_ch12.py`, `tests/test_ch12_more.py` and `tests/test_ch12_extra.py`.
