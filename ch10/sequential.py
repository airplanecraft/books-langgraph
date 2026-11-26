"""Three lookups one after another: each node is its own super-step.
Book: Chapter 10, section 10.1
Run: python ch10/sequential.py
"""
# region: chain
import operator
from typing import Annotated, Callable, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list[str], operator.add]  # ①


def make_step(label: str) -> Callable[[State, RunnableConfig], dict]:
    def step(state: State, config: RunnableConfig) -> dict:
        number = config["metadata"]["langgraph_step"]  # ②
        seen = len(state["notes"])  # ③
        note = f"{label}: super-step {number}, notes seen {seen}"
        return {"notes": [note]}  # ④

    return step


builder = StateGraph(State)
for label in ("read", "order", "plan", "shipping", "draft"):
    builder.add_node(label, make_step(label))
builder.add_edge(START, "read")
builder.add_edge("read", "order")
builder.add_edge("order", "plan")
builder.add_edge("plan", "shipping")
builder.add_edge("shipping", "draft")
builder.add_edge("draft", END)
graph: CompiledStateGraph = builder.compile()

result = graph.invoke({"customer": "Ana", "notes": []})
for note in result["notes"]:
    print(note)
# endregion
