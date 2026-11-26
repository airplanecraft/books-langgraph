"""Exercise 1.3: a three-node graph with a clean node, and its edge list.
Book: Chapter 1, section 1.5
Run: python solutions/ch01_ex3.py
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def clean(state: State) -> dict:
    return {"body": state["body"].strip().lower()}


def classify(state: State) -> dict:
    category = "billing" if "charged" in state["body"] else "other"
    return {"category": category}


def draft(state: State) -> dict:
    name, topic = state["customer"], state["category"]
    return {"reply": f"Hi {name}, we are checking your {topic} question."}


builder = StateGraph(State)
builder.add_node("clean", clean)
builder.add_node("classify", classify)
builder.add_node("draft", draft)
builder.add_edge(START, "clean")
builder.add_edge("clean", "classify")
builder.add_edge("classify", "draft")
builder.add_edge("draft", END)
graph = builder.compile()

ticket = {"customer": "Ana", "body": "  I was CHARGED twice.  ",
          "category": "unknown", "reply": ""}
result = graph.invoke(ticket)
print(result["body"])
print(result["category"])
print([(edge.source, edge.target) for edge in graph.get_graph().edges])
