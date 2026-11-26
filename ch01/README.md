# Chapter 1: Your first graph

Code for chapter 1. Run every script from the top folder of the repository, for example `python ch01/two_nodes.py`. Only `model_node.py` calls a model; run it with `OFFLINE=1` to replay the saved reply. The other scripts need no key and no network.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `state_dict.py` | 1.1 | A `TypedDict` class lists the keys; a ticket is a plain dictionary | `python ch01/state_dict.py` |
| `plain_nodes.py` | 1.2 | Two nodes as plain functions, with the slips copied onto the ticket by hand | `python ch01/plain_nodes.py` |
| `two_nodes.py` | 1.3 | The same two nodes in a graph: `StateGraph`, `add_node`, `add_edge`, `compile`, `invoke` | `python ch01/two_nodes.py` |
| `draw.py` | 1.4 | `get_graph()`, the node and edge lists, `draw_mermaid()` (builds the graph of Listing 1.3 first) | `python ch01/draw.py` |
| `model_node.py` | 1.5 | A node that asks the chat model for the reply | `OFFLINE=1 python ch01/model_node.py` |
| `mistakes.py` | 1.6 | A typo in an edge, no edge from `START`, `invoke` on the builder | `python ch01/mistakes.py` |
| `no_return.py` | 1.7 | A node that forgets to return its slip | `python ch01/no_return.py` |
| `two_runs.py` | 1.8 | Two `invoke` calls on one graph: the second does not see what the first wrote | `python ch01/two_runs.py` |
| `quiz_order.py`, `quiz_unchanged.py`, `quiz_edges.py` | self-check | Runs behind the predict questions  | `python ch01/quiz_order.py` |

Key output of `two_nodes.py`: `reply = 'Hi Ana, we are checking your billing question.'`

Exercises are in the book. Reference solutions: `solutions/ch01_ex1.py`, `solutions/ch01_ex2.py`, `solutions/ch01_ex3.py`. Tests: `tests/test_ch01.py` and `tests/test_ch01_more.py`.
