"""Self-check run: a node returns a key with a typo in its name.
Book: Chapter 2, section 2.1
Run: python ch02/quiz_typo.py
"""
# region: typo
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    category: str


def classify(state: State) -> dict:
    return {"catgory": "billing"}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)
start = {"customer": "Ana", "category": "unknown"}
print(builder.compile().invoke(start))
# endregion
