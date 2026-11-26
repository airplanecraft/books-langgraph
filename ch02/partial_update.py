"""Show that a node returns an update and keys it leaves out stay as they are.
Book: Chapter 2, section 2.2
Run: python ch02/partial_update.py
"""
# region: partial
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    category: str


def classify(state: State) -> dict:
    print("node sees:    ", state)  # ①
    update = {"category": "billing"}  # ②
    print("node returns: ", update)
    return update


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)
graph = builder.compile()

start = {"customer": "Ana", "category": "unknown"}
print("state after:  ", graph.invoke(start))  # ③
# endregion
