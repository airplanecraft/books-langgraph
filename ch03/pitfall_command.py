"""A node that returns a Command without a return type: edges are not drawn.
Book: Chapter 3, section 3.6
Run: python ch03/pitfall_command.py
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


# region: bare
def classify(state: State):  # ①
    billing = "charged" in state["body"]
    category = "billing" if billing else "other"
    target = "billing_reply" if billing else "general_reply"
    return Command(update={"category": category}, goto=target)
# endregion


def billing_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, we are checking the charge."}


def general_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, thanks for your email."}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing_reply", billing_reply)
builder.add_node("general_reply", general_reply)
builder.add_edge(START, "classify")
builder.add_edge("billing_reply", END)
builder.add_edge("general_reply", END)
graph = builder.compile()

ticket = {"customer": "Ana", "body": "I was charged twice for order B42.",
          "category": "unknown", "reply": ""}
result = graph.invoke(ticket)
print(result["category"], "|", result["reply"])
edges = graph.get_graph().edges
for edge in sorted((e.source, e.target, e.conditional) for e in edges):
    print(edge)
