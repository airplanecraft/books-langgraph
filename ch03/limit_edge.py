"""Three node runs: limit 3 runs them all, then raises.
Book: Chapter 3, section 3.4
Run: python ch03/limit_edge.py
"""
# region: edge
from typing import Literal, TypedDict

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


def add_one(state: State) -> dict:
    count = state["count"] + 1
    print("add_one ran, count is now", count)  # ①
    return {"count": count}


def after_add(state: State) -> Literal["add_one", "__end__"]:
    return END if state["count"] >= 3 else "add_one"


builder = StateGraph(State)
builder.add_node("add_one", add_one)
builder.add_edge(START, "add_one")
builder.add_conditional_edges("add_one", after_add)
graph = builder.compile()

for limit in (3, 4):
    print("limit", limit)
    try:
        graph.invoke({"count": 0}, config={"recursion_limit": limit})
        print("finished")  # ②
    except GraphRecursionError:
        print("GraphRecursionError")
# endregion
