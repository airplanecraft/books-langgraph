"""Fan-out: one node with three edges leaving it; the three targets share a super-step.
Book: Chapter 10, section 10.2
Run: python ch10/parallel.py
"""
import operator
from typing import Annotated, Callable, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


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


# region: fan_out
builder = StateGraph(State)
for label in ("read", "order", "plan", "shipping", "draft"):
    builder.add_node(label, make_step(label))
builder.add_edge(START, "read")
for label in ("order", "plan", "shipping"):
    builder.add_edge("read", label)  # ①
    builder.add_edge(label, "draft")  # ②
builder.add_edge("draft", END)
graph: CompiledStateGraph = builder.compile()

result = graph.invoke({"customer": "Ana", "notes": []})
for note in result["notes"]:
    print(note)
# endregion
