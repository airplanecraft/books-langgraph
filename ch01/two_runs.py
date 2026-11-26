"""Invoke one graph twice: the second run does not see what the first one wrote.
Book: Chapter 1, section 1.7
Run: python ch01/two_runs.py
"""
# region: runs
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    category: str
    reply: str


def classify(state: State) -> dict:
    print("classify starts with", state)  # ①
    return {"category": "billing", "reply": "Hi " + state["customer"]}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)
graph = builder.compile()

graph.invoke({"customer": "Ana", "category": "unknown"})  # ②
graph.invoke({"customer": "Ben", "category": "unknown"})  # ③
# endregion
