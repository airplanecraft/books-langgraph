"""Self-check run: two parallel nodes add to one number with a reducer.
Book: Chapter 10, section 10.3
Run: python ch10/quiz_total.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    total: Annotated[int, operator.add]


def base(state: State) -> None:
    return None


def fee(state: State) -> dict:
    return {"total": 10}


def tax(state: State) -> dict:
    return {"total": 5}


builder = StateGraph(State)
for name, node in (("base", base), ("fee", fee), ("tax", tax)):
    builder.add_node(name, node)
builder.add_edge(START, "base")
builder.add_edge("base", "fee")
builder.add_edge("base", "tax")
builder.add_edge("fee", END)
builder.add_edge("tax", END)
print(builder.compile().invoke({"total": 100})["total"])
