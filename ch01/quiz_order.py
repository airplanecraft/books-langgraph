"""Self-check run: nodes are added in one order and connected in another.
Book: Chapter 1, section 1.3
Run: python ch01/quiz_order.py
"""
# region: order
from collections.abc import Callable
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    log: str


def make_node(name: str) -> Callable[[State], dict]:
    def node(state: State) -> dict:
        return {"log": state["log"] + name + ","}

    return node


builder = StateGraph(State)
builder.add_node("second", make_node("second"))
builder.add_node("first", make_node("first"))
builder.add_edge(START, "first")
builder.add_edge("first", "second")
builder.add_edge("second", END)
print(builder.compile().invoke({"log": ""}))
# endregion
