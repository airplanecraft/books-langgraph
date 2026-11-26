"""Self-check run: a node returns a Command with an update and a goto.
Book: Chapter 3, section 3.5
Run: python ch03/quiz_command.py
"""
# region: command
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    customer: str
    category: str
    reply: str


def sort(state: State) -> Command[Literal["slow", "fast"]]:
    return Command(update={"category": "refund"}, goto="fast")


def slow(state: State) -> dict:
    return {"reply": "slow"}


def fast(state: State) -> dict:
    return {"reply": "fast"}


builder = StateGraph(State)
builder.add_node("sort", sort)
builder.add_node("slow", slow)
builder.add_node("fast", fast)
builder.add_edge(START, "sort")
builder.add_edge("slow", END)
builder.add_edge("fast", END)
ticket = {"customer": "Ana", "category": "unknown", "reply": ""}
print(builder.compile().invoke(ticket))
# endregion
