"""Self-check run for chapter 7: which prints happen again after a resume.
Book: Chapter 7, section 7.4
Run: python ch07/quiz_prepare.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


calls: list = []


class State(TypedDict):
    answer: str


def look_up(state: State) -> dict:
    calls.append("look_up")
    return {}


def confirm(state: State) -> dict:
    calls.append("confirm")
    answer = interrupt("Go on?")
    return {"answer": answer}


builder = StateGraph(State)
builder.add_node("look_up", look_up)
builder.add_node("confirm", confirm)
builder.add_edge(START, "look_up")
builder.add_edge("look_up", "confirm")
builder.add_edge("confirm", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "q"}}
graph.invoke({"answer": ""}, config)
graph.invoke(Command(resume="yes"), config)
print(calls)
