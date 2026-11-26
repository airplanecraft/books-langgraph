"""Self-check run: a deferred node waits for a branch that does not lead to it.
Book: Chapter 10, section 10.5
Run: python ch10/quiz_waits.py
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
for label in ("scan", "fast", "slow_1", "slow_2"):
    builder.add_node(label, make_node(label))
builder.add_node("close", make_node("close"), defer=True)
builder.add_edge(START, "scan")
builder.add_edge("scan", "fast")
builder.add_edge("scan", "slow_1")
builder.add_edge("slow_1", "slow_2")
builder.add_edge("slow_2", END)
builder.add_edge("fast", "close")
builder.add_edge("close", END)
log = builder.compile().invoke({"log": []})["log"]
print([entry for entry in log if entry.startswith("close")])
