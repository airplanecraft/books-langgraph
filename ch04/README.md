# Chapter 4: An agent, built by hand

Code for chapter 4. Run every script from the top folder of the repository, for example `python ch04/tool_node.py`. Only `model_node.py`, `agent_by_hand.py` and `two_orders.py` call a model, and `OFFLINE=1 python ch04/agent_by_hand.py` replays them; the others use the stand-in model of chapter 0 or no model, and need no key and no network.

| File | Listing | What it shows | Run |
|---|---|---|---|
| `model_node.py` | 4.1 | The tool of section 0.4 | `OFFLINE=1 python ch04/model_node.py` |
| `model_node.py` | 4.2 | A graph whose model node asks for a tool; nobody answers | `OFFLINE=1 python ch04/model_node.py` |
| `tool_node.py` | 4.3 | A tool node answers the tool call of the latest AI message | `python ch04/tool_node.py` |
| `agent_by_hand.py` | 4.4, 4.5 | Model node, tool node and a routing function make the agent loop; the run | `OFFLINE=1 python ch04/agent_by_hand.py` |
| `tools_condition.py` | 4.6, 4.7 | The `build` helper; own `route` next to `tools_condition` | `python ch04/tools_condition.py` |
| `runaway.py` | 4.8 | A model that always asks for a tool stops at the recursion limit | `python ch04/runaway.py` |
| `trace_messages.py` | 4.9 | The message list the model node receives, round by round | `python ch04/trace_messages.py` |
| `two_orders.py` | 4.10 | A real model asks for two tools in one reply | `OFFLINE=1 python ch04/two_orders.py` |
| `two_calls.py` | 4.11 | Two tool calls in one reply, two tool messages | `python ch04/two_calls.py` |
| `bad_args.py` | 4.12 | A bad request becomes a tool message | `python ch04/bad_args.py` |
| `raises.py` | 4.13 | An exception in a tool stops the run | `python ch04/raises.py` |
| `pitfall_edge.py` | 4.14 | No edge back from the tool node | `python ch04/pitfall_edge.py` |
| `pitfall_name.py` | 4.15 | A tool node that is not named `tools` | `python ch04/pitfall_name.py` |
| `quiz_rounds.py`, `quiz_three_calls.py`, `quiz_bad_args.py` | self-check | Runs behind the predict questions | `python ch04/quiz_rounds.py` |

Key output of `trace_messages.py`: `final 6 ['human', 'ai', 'tool', 'ai', 'tool', 'ai']`

Exercises are in the book. Reference solutions: `solutions/ch04_ex1.py`, `solutions/ch04_ex2.py`, `solutions/ch04_ex3.py`. Tests: `tests/test_ch04.py` and `tests/test_ch04_more.py`.
