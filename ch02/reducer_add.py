"""Show a reducer: notes is declared with operator.add, so updates are added.
Book: Chapter 2, section 2.3
Run: python ch02/reducer_add.py
"""
# region: reducer
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list[str], operator.add]  # ①


def read(state: State) -> dict:
    return {"notes": ["read"]}  # ②


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

print(graph.invoke({"customer": "Ana", "notes": ["received"]}))  # ③
# endregion
