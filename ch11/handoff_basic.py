"""The smallest handoff: a node in a subgraph names a node of the parent graph.
Book: Chapter 11, section 11.6
Run: python ch11/handoff_basic.py
"""
# region: basic
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class Ticket(TypedDict):
    log: Annotated[list[str], operator.add]


def hand_over(state: Ticket) -> Command:  # ①
    return Command(graph=Command.PARENT, goto="billing",
                   update={"log": ["support: pass to billing"]})


def billing(state: Ticket) -> dict:
    return {"log": ["billing: refund noted"]}


inner = StateGraph(Ticket)
inner.add_node("hand_over", hand_over)
inner.add_edge(START, "hand_over")
support = inner.compile()

outer = StateGraph(Ticket)
outer.add_node("support", support, destinations=("billing",))  # ②
outer.add_node("billing", billing)
outer.add_edge(START, "support")
outer.add_edge("billing", END)
graph = outer.compile()

print(graph.invoke({"log": ["start"]})["log"])  # ③
edges = [(edge.source, edge.target) for edge in graph.get_graph().edges]
print(sorted(edges))  # ④
# endregion
