"""Optional: look up the order and the customer's history side by side.
Book: Chapter 13, section 13.7
Run: python ch13/optional_parallel.py
"""
# region: parallel
import operator
from typing import Annotated, Callable, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    notes: Annotated[list, operator.add]  # ①


def make_step(name: str) -> Callable[[State, RunnableConfig], dict]:
    def step(state: State, config: RunnableConfig) -> dict:
        number = config["metadata"]["langgraph_step"]  # ②
        return {"notes": [f"{name} ran in super-step {number}"]}

    return step


builder = StateGraph(State)
for name in ("lookup", "history", "draft"):
    builder.add_node(name, make_step(name))
builder.add_edge(START, "lookup")  # ③
builder.add_edge(START, "history")
builder.add_edge("lookup", "draft")
builder.add_edge("history", "draft")
builder.add_edge("draft", END)
graph = builder.compile()

result = graph.invoke({"notes": []})
for note in sorted(result["notes"]):  # ④
    print(note)
# endregion
