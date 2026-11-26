"""Exercise 10.2: let two parallel nodes write one key by giving it a reducer.
Book: Chapter 10, section 10.3
Run: python solutions/ch10_ex2.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    reply: Annotated[list[str], operator.add]


def read(state: State) -> None:
    return None


def order(state: State) -> dict:
    return {"reply": ["from order"]}


def plan(state: State) -> dict:
    return {"reply": ["from plan"]}


builder = StateGraph(State)
for name, node in (("read", read), ("order", order), ("plan", plan)):
    builder.add_node(name, node)
builder.add_edge(START, "read")
builder.add_edge("read", "order")
builder.add_edge("read", "plan")
builder.add_edge("order", END)
builder.add_edge("plan", END)
print(sorted(builder.compile().invoke({"reply": []})["reply"]))
