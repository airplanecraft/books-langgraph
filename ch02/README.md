# Chapter 2: State and reducers

Code for chapter 2. Run every script from the top folder of the repository, for example `OFFLINE=1 python ch02/reducer_add.py`. Only `chat_node.py` calls a model; the others need no key and no network.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `schema_filter.py` | 2.1 | A key outside the schema is dropped; types are not checked | `python ch02/schema_filter.py` |
| `partial_update.py` | 2.2 | A node returns an update; other keys stay | `python ch02/partial_update.py` |
| `return_kinds.py` | 2.3 | A dictionary, `{}`, `None` and a list as node results | `python ch02/return_kinds.py` |
| `replace.py` | 2.4 | No reducer: the new value replaces the old one | `python ch02/replace.py` |
| `reducer_add.py` | 2.5 | `operator.add` as a reducer | `python ch02/reducer_add.py` |
| `custom_reducer.py` | 2.6 | Your own reducer, `keep_max` | `python ch02/custom_reducer.py` |
| `add_messages.py` | 2.7 | Append, replace by id, dictionary to message | `python ch02/add_messages.py` |
| `chat_node.py` | 2.8 | `MessagesState` and a node that calls the model | `OFFLINE=1 python ch02/chat_node.py` |
| `ticket.py` | 2.9 | One state with a rule for each key | `python ch02/ticket.py` |
| `pitfalls.py` | 2.10 | Whole list returned, empty list returned, `Overwrite` | `python ch02/pitfalls.py` |
| `edit_in_place.py` | 2.11 | A node edits the state in place | `python ch02/edit_in_place.py` |
| `missing_input.py` | 2.12 | A key left out of the input | `python ch02/missing_input.py` |
| `quiz_total.py`, `quiz_extra_key.py`, `quiz_ids.py`, `quiz_reducer_order.py`, `quiz_typo.py`, `quiz_whole_list.py` | self-check | Runs behind the predict questions | `python ch02/quiz_total.py` |
| `first_value.py` | section 2.3 | A type with no empty value skips the reducer for its first value (output not printed in the book) | `python ch02/first_value.py` |

Key output of `ticket.py`: `urgency   3`

Exercises are in the book. Reference solutions: `solutions/ch02_ex1.py`, `solutions/ch02_ex2.py`, `solutions/ch02_ex3.py`. Tests: `tests/test_ch02.py` and `tests/test_ch02_more.py`.
