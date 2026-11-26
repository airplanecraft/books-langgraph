"""Self-check run for chapter 7: two interrupts in one node, resumed twice.
Book: Chapter 7, section 7.8
Run: python ch07/quiz_two.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

log: list = []


class State(TypedDict):
    done: bool


def ask_twice(state: State) -> dict:
    first = interrupt("a?")
    log.append(f"got {first}")
    second = interrupt("b?")
    log.append(f"got {second}")
    return {"done": True}


builder = StateGraph(State)
builder.add_node("ask_twice", ask_twice)
builder.add_edge(START, "ask_twice")
builder.add_edge("ask_twice", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "q"}}
graph.invoke({"done": False}, config)
graph.invoke(Command(resume="x"), config)
graph.invoke(Command(resume="y"), config)
print(log)
