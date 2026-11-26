"""Show that keys outside the state schema are dropped and types go unchecked.
Book: Chapter 2, section 2.1
Run: python ch02/schema_filter.py
"""
# region: schema
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):  # ①
    customer: str
    category: str


def classify(state: State) -> dict:
    # "mood" is not in State, and 42 is not a str
    return {"category": 42, "mood": "angry"}  # ②


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)
graph = builder.compile()

start = {"customer": "Ana", "category": "unknown", "channel": "email"}  # ③
print(graph.invoke(start))
# endregion
