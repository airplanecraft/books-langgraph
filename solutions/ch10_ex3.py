"""Exercise 10.3: one lookup run per order number with Send objects.
Book: Chapter 10, section 10.6
Run: python solutions/ch10_ex3.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

STATUS = {"A17": "shipped", "B42": "delayed", "C03": "shipped"}


class State(TypedDict):
    orders: list[str]
    results: Annotated[list[str], operator.add]
    summary: str


def fan_out(state: State) -> list[Send]:
    return [Send("lookup", {"order": order}) for order in state["orders"]]


def lookup(item: dict) -> dict:
    return {"results": [f"{item['order']}: {STATUS[item['order']]}"]}


def summarize(state: State) -> dict:
    shipped = sum(1 for line in state["results"] if line.endswith("shipped"))
    return {"summary": f"{shipped} shipped"}


builder = StateGraph(State)
builder.add_node("lookup", lookup)
builder.add_node("summarize", summarize)
builder.add_conditional_edges(START, fan_out, ["lookup"])
builder.add_edge("lookup", "summarize")
builder.add_edge("summarize", END)
result = builder.compile().invoke(
    {"orders": ["C03", "A17", "B42"], "results": [], "summary": ""})
print(sorted(result["results"]))
print(result["summary"])
