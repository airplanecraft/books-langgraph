"""A node returns a Command: it updates the state and picks the next node.
Book: Chapter 3, section 3.5
Run: python ch03/command_goto.py
"""
# region: node
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def classify(
    state: State,
) -> Command[Literal["billing_reply", "general_reply"]]:  # ①
    billing = "charged" in state["body"]
    category = "billing" if billing else "other"
    target = "billing_reply" if billing else "general_reply"
    return Command(update={"category": category}, goto=target)  # ②
# endregion


def billing_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, we are checking the charge."}


def general_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, thanks for your email."}


# region: build
builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing_reply", billing_reply)
builder.add_node("general_reply", general_reply)
builder.add_edge(START, "classify")
builder.add_edge("billing_reply", END)
builder.add_edge("general_reply", END)
graph = builder.compile()  # ①

ticket = {"customer": "Ana", "body": "I was charged twice for order B42.",
          "category": "unknown", "reply": ""}
result = graph.invoke(ticket)
print(result["category"], "|", result["reply"])
edges = graph.get_graph().edges
for edge in sorted((e.source, e.target, e.conditional) for e in edges):
    print(edge)  # ②
# endregion
