"""A node that computes a value but forgets to return it.
Book: Chapter 1, section 1.7
Run: python ch01/no_return.py
"""
# region: forgot
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    category: str


def classify(state: State) -> dict:
    category = "billing"
    print("classify worked out:", category)  # ①


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)
print(builder.compile().invoke({"category": "unknown"}))  # ②
# endregion
