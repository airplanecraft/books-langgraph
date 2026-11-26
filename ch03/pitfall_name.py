"""A wrong node name from a routing function or a Command.
Book: Chapter 3, section 3.6
Run: python ch03/pitfall_name.py
"""
from typing import Any, Callable, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    customer: str
    category: str
    reply: str


def billing_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, we are checking the charge."}


def general_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, thanks for your email."}


# region: typo
def classify(state: State) -> dict:
    return {"category": "billing"}


def route_plain(state: State):
    return "billing_replay"  # ①


def route_literal(state: State) -> Literal["billing_reply", "general_reply"]:
    return "billing_replay"  # ②


def classify_command(
    state: State,
) -> Command[Literal["billing_reply", "general_reply"]]:
    return Command(goto="billing_replay")  # ③


def build(first: Callable, route: Callable | None = None) -> Any:
    builder = StateGraph(State)
    builder.add_node("first", first)
    builder.add_node("billing_reply", billing_reply)
    builder.add_node("general_reply", general_reply)
    builder.add_edge(START, "first")
    if route:
        builder.add_conditional_edges("first", route)
    builder.add_edge("billing_reply", END)
    builder.add_edge("general_reply", END)
    return builder.compile()


ticket = {"customer": "Ana", "category": "unknown", "reply": ""}
cases = {"plain": build(classify, route_plain),
         "literal": build(classify, route_literal),
         "command": build(classify_command)}
for name, graph in cases.items():
    try:
        print(name, "| reply:", repr(graph.invoke(ticket)["reply"]))  # ④
    except KeyError as error:
        print(name, "| KeyError:", error)
# endregion
