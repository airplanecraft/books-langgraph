"""Solution 3 of chapter 11: a support agent that hands refunds to billing.
Book: Chapter 11, section 11.6
Run: python solutions/ch11_ex3.py
"""
from typing import TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import Command


class Ticket(TypedDict):
    text: str
    owner: str


def triage(state: Ticket) -> Command | dict:
    if "refund" in state["text"]:
        return Command(graph=Command.PARENT, goto="billing")
    return {"owner": "support"}


def billing(state: Ticket) -> dict:
    return {"owner": "billing"}


inner = StateGraph(Ticket)
inner.add_node("triage", triage)
inner.add_edge(START, "triage")
outer = StateGraph(Ticket)
outer.add_node("support", inner.compile(), destinations=("billing",))
outer.add_node("billing", billing)
outer.add_edge(START, "support")
graph = outer.compile()

for text in ("Please refund order A17.", "Where is order B42?"):
    print(graph.invoke({"text": text, "owner": ""})["owner"])
