"""Self-check run: a loop of four node runs at two recursion limits.
Book: Chapter 3, section 3.4
Run: python ch03/quiz_limit.py
"""
# region: limit
from typing import Literal, TypedDict

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


def add_one(state: State) -> dict:
    return {"count": state["count"] + 1}


def after_add(state: State) -> Literal["add_one", "__end__"]:
    return END if state["count"] >= 4 else "add_one"


builder = StateGraph(State)
builder.add_node("add_one", add_one)
builder.add_edge(START, "add_one")
builder.add_conditional_edges("add_one", after_add)
graph = builder.compile()

for limit in (4, 5):
    try:
        graph.invoke({"count": 0}, config={"recursion_limit": limit})
        print(f"limit {limit}: finished")
    except GraphRecursionError:
        print(f"limit {limit}: GraphRecursionError")
# endregion
