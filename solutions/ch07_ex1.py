"""Exercise 7.1: the print before the interrupt moves into a node of its own.
Book: Chapter 7, section 7.4
Run: python solutions/ch07_ex1.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    answers: list


def announce(state: State) -> dict:
    print("announce runs")
    return {}


def collect(state: State) -> dict:
    order = interrupt("Which order?")
    print("first answer:", order)
    reason = interrupt("Which reason?")
    print("second answer:", reason)
    return {"answers": [order, reason]}


builder = StateGraph(State)
builder.add_node("announce", announce)
builder.add_node("collect", collect)
builder.add_edge(START, "announce")
builder.add_edge("announce", "collect")
builder.add_edge("collect", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
result = graph.invoke({"answers": []}, config)
print("asked:", result["__interrupt__"][0].value)
result = graph.invoke(Command(resume="B42"), config)
print("asked:", result["__interrupt__"][0].value)
result = graph.invoke(Command(resume="late"), config)
print("final:", result["answers"])
