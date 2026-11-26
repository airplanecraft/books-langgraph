"""Write your own reducer: a function of the old value and the new value.
Book: Chapter 2, section 2.3
Run: python ch02/custom_reducer.py
"""
# region: keep_max
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


def keep_max(old: int, new: int) -> int:  # ①
    print(f"keep_max(old={old}, new={new})")
    return max(old, new)


class State(TypedDict):
    customer: str
    urgency: Annotated[int, keep_max]  # ②


def read(state: State) -> dict:
    return {"urgency": 3}


def draft(state: State) -> dict:
    return {"urgency": 2}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("draft", draft)
builder.add_edge(START, "read")
builder.add_edge("read", "draft")
builder.add_edge("draft", END)
graph = builder.compile()

print(graph.invoke({"customer": "Ana", "urgency": 1}))
# endregion
