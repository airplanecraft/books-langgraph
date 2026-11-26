"""Self-check run: copies left by a failed run under durability="exit".
Book: Chapter 9, section 9.6
Run: python ch09/quiz_copies.py
"""
# region: quiz
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    order: str


def pack(state: State) -> dict:
    return {}


def ship(state: State) -> dict:
    raise ConnectionError("carrier unreachable")


builder = StateGraph(State)
for name in ("check", "pick", "pack"):
    builder.add_node(name, pack)
builder.add_node("ship", ship)
builder.add_edge(START, "check")
builder.add_edge("check", "pick")
builder.add_edge("pick", "pack")
builder.add_edge("pack", "ship")
builder.add_edge("ship", END)
graph = builder.compile(checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "o1"}}
try:
    graph.invoke({"order": "A17"}, config, durability="exit")
except ConnectionError:
    pass
copies = len(list(graph.get_state_history(config)))
print(copies, graph.get_state(config).next)
# endregion
