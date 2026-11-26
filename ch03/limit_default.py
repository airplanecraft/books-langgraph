"""Without recursion_limit in the config, a loop stops at 10,007 super-steps.
Book: Chapter 3, section 3.4
Run: python ch03/limit_default.py
"""
# region: default
from typing import Literal, TypedDict

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int
    stop_at: int


def add_one(state: State) -> dict:
    return {"count": state["count"] + 1}


def after_add(state: State) -> Literal["add_one", "__end__"]:
    return END if state["count"] >= state["stop_at"] else "add_one"


builder = StateGraph(State)
builder.add_node("add_one", add_one)
builder.add_edge(START, "add_one")
builder.add_conditional_edges("add_one", after_add)
graph = builder.compile()

for stop_at in (10006, 10007):
    try:
        result = graph.invoke({"count": 0, "stop_at": stop_at})  # ①
        print(f"{stop_at} node runs: finished with count {result['count']}")
    except GraphRecursionError:
        print(f"{stop_at} node runs: GraphRecursionError")
# endregion
