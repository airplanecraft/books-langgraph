"""Self-check run: the smallest recursion limit of a graph with two long branches.
Book: Chapter 10, section 10.2
Run: python ch10/quiz_limit.py
"""
import operator
from typing import Annotated, Callable, TypedDict

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    log: Annotated[list[str], operator.add]


def make_node(label: str) -> Callable[[State], dict]:
    def node(state: State) -> dict:
        return {"log": [label]}

    return node


builder = StateGraph(State)
for label in ("scan", "left_1", "left_2", "right_1", "right_2", "join"):
    builder.add_node(label, make_node(label))
builder.add_edge(START, "scan")
builder.add_edge("scan", "left_1")
builder.add_edge("scan", "right_1")
builder.add_edge("left_1", "left_2")
builder.add_edge("right_1", "right_2")
builder.add_edge(["left_2", "right_2"], "join")
builder.add_edge("join", END)
graph = builder.compile()

for limit in range(1, 10):
    try:
        graph.invoke({"log": []}, config={"recursion_limit": limit})
    except GraphRecursionError:
        continue
    print("smallest limit that finishes:", limit)
    break
