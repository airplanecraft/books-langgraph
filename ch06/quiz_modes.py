"""Self-check run: the order of items when two modes are streamed together.
Book: Chapter 6, section 6.5
Run: python ch06/quiz_modes.py
"""
# region: quiz
from typing import TypedDict

from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    total: int


def first(state: State) -> dict:
    write = get_stream_writer()
    write("one")
    write("two")
    return {"total": 1}


def second(state: State) -> dict:
    get_stream_writer()("three")
    return {"total": 2}


builder = StateGraph(State)
builder.add_node("first", first)
builder.add_node("second", second)
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", END)
graph = builder.compile()

items = graph.stream({"total": 0}, stream_mode=["custom", "updates"])
print(" ".join(mode for mode, data in items))
# endregion
