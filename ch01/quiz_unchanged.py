"""Self-check run: each node returns one key of a three-key state.
Book: Chapter 1, section 1.2
Run: python ch01/quiz_unchanged.py
"""
# region: unchanged
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    a: int
    b: int
    c: int


def first(state: State) -> dict:
    return {"a": state["a"] + 1}


def second(state: State) -> dict:
    return {"b": state["a"] + 10}


builder = StateGraph(State)
builder.add_node("first", first)
builder.add_node("second", second)
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", END)
print(builder.compile().invoke({"a": 0, "b": 0, "c": 0}))
# endregion
