"""Self-check run: a node returns a key in the schema and one that is not.
Book: Chapter 2, section 2.1
Run: python ch02/quiz_extra_key.py
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


# region: extra
class State(TypedDict):
    a: int
    b: int


def node(state: State) -> dict:
    return {"b": 1, "c": 2}


builder = StateGraph(State)
builder.add_node("node", node)
builder.add_edge(START, "node")
builder.add_edge("node", END)
print(builder.compile().invoke({"a": 0, "b": 0}))
# endregion
