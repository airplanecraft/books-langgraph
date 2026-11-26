"""Mistake: a list of one mode gives tuples, not plain items
Book: Chapter 6, section 6.6
Run: python ch06/pitfall_shape.py
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
# endregion

# region: pitfall_shape
one = list(graph.stream(start, stream_mode="updates"))  # ①
many = list(graph.stream(start, stream_mode=["updates"]))  # ②
print(type(one[0]).__name__, one[0])
print(type(many[0]).__name__, many[0])
# endregion
