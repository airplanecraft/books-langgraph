"""Exercise 10.1: a fourth lookup that runs in the same super-step as the others.
Book: Chapter 10, section 10.2
Run: python solutions/ch10_ex1.py
"""
import operator
from typing import Annotated, Callable, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list[str], operator.add]


def make_step(label: str) -> Callable[[State, RunnableConfig], dict]:
    def step(state: State, config: RunnableConfig) -> dict:
        number = config["metadata"]["langgraph_step"]
        seen = len(state["notes"])
        note = f"{label}: super-step {number}, notes seen {seen}"
        return {"notes": [note]}

    return step


lookups = ("order", "plan", "shipping", "refund")
builder = StateGraph(State)
for label in ("read", *lookups, "draft"):
    builder.add_node(label, make_step(label))
builder.add_edge(START, "read")
for label in lookups:
    builder.add_edge("read", label)
    builder.add_edge(label, "draft")
builder.add_edge("draft", END)
result = builder.compile().invoke({"customer": "Ana", "notes": []})
print([note for note in result["notes"] if note.startswith("draft")][0])
