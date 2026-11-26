"""Handoff mistakes: no destinations, an extra edge, a Literal type, a lone subgraph.
Book: Chapter 11, section 11.9
Run: python ch11/handoff_pitfalls.py
"""
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


# region: pitfalls
from typing import Literal
from langgraph.errors import ParentCommand


def build(destinations: tuple | None, extra_edge: bool) -> object:
    outer = StateGraph(Ticket)
    outer.add_node("support", support, destinations=destinations)  # ①
    outer.add_node("billing", billing)
    outer.add_node("report", lambda state: {"log": ["report: ran"]})
    outer.add_edge(START, "support")
    outer.add_edge("billing", END)
    if extra_edge:
        outer.add_edge("support", "report")  # ②
    return outer.compile()

for destinations, extra_edge in ((None, False), (("billing",), True)):
    graph = build(destinations, extra_edge)
    edges = [(edge.source, edge.target) for edge in graph.get_graph().edges]
    print(graph.invoke({"log": []})["log"], sorted(edges))  # ③

def typed(state: Ticket) -> Command[Literal["billing"]]:  # ④
    return Command(graph=Command.PARENT, goto="billing")

bad = StateGraph(Ticket)
bad.add_node("hand_over", typed)
bad.add_edge(START, "hand_over")
try:
    bad.compile()
except ValueError as error:
    print("compile:", error)
try:
    support.invoke({"log": []})  # ⑤
except ParentCommand as error:
    print("alone:", type(error).__name__)
# endregion
