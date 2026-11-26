"""Nodes that write nothing: updates still reports them, values stays silent.
Book: Chapter 6, section 6.2
Run: python ch06/quiet.py
"""
# region: quiet
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


def read(state: State) -> dict:
    return {"count": state["count"] + 1}


def look(state: State) -> None:  # ①
    """Reads the state and changes nothing."""


def tidy(state: State) -> dict:  # ②
    return {}


def save(state: State) -> dict:
    return {"count": state["count"] + 1}


builder = StateGraph(State)
for node in (read, look, tidy, save):
    builder.add_node(node)
builder.add_edge(START, "read")
builder.add_edge("read", "look")
builder.add_edge("look", "tidy")
builder.add_edge("tidy", "save")
builder.add_edge("save", END)
graph = builder.compile()

start = {"count": 0}
for item in graph.stream(start, stream_mode="updates"):  # ③
    print("updates:", item)
for state in graph.stream(start, stream_mode="values"):  # ④
    print("values:", state)
# endregion
