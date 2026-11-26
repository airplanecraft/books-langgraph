"""Self-check run: a join with separate edges and branches of unequal length.
Book: Chapter 10, section 10.4
Run: python ch10/quiz_steps.py
"""
import operator
from typing import Annotated, Callable, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    log: Annotated[list[str], operator.add]


def make_node(label: str) -> Callable[[State, RunnableConfig], dict]:
    def node(state: State, config: RunnableConfig) -> dict:
        return {"log": [f"{label}:{config['metadata']['langgraph_step']}"]}

    return node


builder = StateGraph(State)
for label in ("scan", "left", "right_1", "right_2", "join"):
    builder.add_node(label, make_node(label))
builder.add_edge(START, "scan")
builder.add_edge("scan", "left")
builder.add_edge("scan", "right_1")
builder.add_edge("right_1", "right_2")
builder.add_edge("left", "join")
builder.add_edge("right_2", "join")
builder.add_edge("join", END)
log = builder.compile().invoke({"log": []})["log"]
print([entry for entry in log if entry.startswith("join")])
