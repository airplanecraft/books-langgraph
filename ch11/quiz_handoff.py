"""Self-check run: what the parent keeps when a subgraph hands over.
Book: Chapter 11, section 11.6
Run: python ch11/quiz_handoff.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class Ticket(TypedDict):
    notes: Annotated[list[str], operator.add]


def first(state: Ticket) -> dict:
    return {"notes": ["a"]}


def second(state: Ticket) -> Command:
    return Command(graph=Command.PARENT, goto="billing",
                   update={"notes": ["b"]})


def billing(state: Ticket) -> dict:
    return {"notes": ["c"]}


inner = StateGraph(Ticket)
inner.add_node("first", first)
inner.add_node("second", second)
inner.add_edge(START, "first")
inner.add_edge("first", "second")
outer = StateGraph(Ticket)
outer.add_node("support", inner.compile(), destinations=("billing",))
outer.add_node("billing", billing)
outer.add_edge(START, "support")
outer.add_edge("billing", END)
print(outer.compile().invoke({"notes": ["s"]})["notes"])
