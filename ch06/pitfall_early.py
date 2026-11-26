"""Mistake: leaving the loop early stops the run
Book: Chapter 6, section 6.6
Run: python ch06/pitfall_early.py
"""
# region: pitfall_early
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

ran = []  # the names of the nodes that finished


class State(TypedDict):
    count: int


def first(state: State) -> dict:
    ran.append("first")
    return {"count": state["count"] + 1}


def second(state: State) -> dict:
    ran.append("second")
    return {"count": state["count"] + 1}


builder = StateGraph(State)
builder.add_node("first", first)
builder.add_node("second", second)
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", END)
graph = builder.compile()

for stop in (True, False):
    ran.clear()
    for update in graph.stream({"count": 0}, stream_mode="updates"):  # ①
        if stop:
            break  # ②
    print("stopped early:", stop, "| nodes that ran:", ran)
# endregion
