"""Exercise 2.1: find the keys a node returns that the schema does not list.
Book: Chapter 2, section 2.1
Run: python solutions/ch02_ex1.py
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    category: str


def classify(state: State) -> dict:
    update = {"categroy": "billing"}
    dropped = [key for key in update if key not in State.__annotations__]
    print("dropped:", dropped)
    return update


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)

start = {"customer": "Ana", "category": "unknown"}
print(builder.compile().invoke(start))
