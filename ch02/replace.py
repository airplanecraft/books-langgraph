"""Show the default rule: with no reducer, a new value replaces the old one.
Book: Chapter 2, section 2.2
Run: python ch02/replace.py
"""
# region: replace
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: list[str]  # ①


def read(state: State) -> dict:
    return {"notes": ["read"]}


def draft(state: State) -> dict:
    print("draft sees:", state["notes"])
    return {"notes": ["drafted"]}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("draft", draft)
builder.add_edge(START, "read")
builder.add_edge("read", "draft")
builder.add_edge("draft", END)
graph = builder.compile()

print(graph.invoke({"customer": "Ana", "notes": ["received"]}))
# endregion
