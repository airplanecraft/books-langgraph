"""Exercise 1.1: a classify node that also knows the category "shipping".
Book: Chapter 1, section 1.3
Run: python solutions/ch01_ex1.py
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def classify(state: State) -> dict:
    body = state["body"]
    if "charged" in body:
        return {"category": "billing"}
    if "parcel" in body:
        return {"category": "shipping"}
    return {"category": "other"}


def draft(state: State) -> dict:
    name, topic = state["customer"], state["category"]
    return {"reply": f"Hi {name}, we are checking your {topic} question."}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("draft", draft)
builder.add_edge(START, "classify")
builder.add_edge("classify", "draft")
builder.add_edge("draft", END)

ticket = {"customer": "Ben", "body": "Where is my parcel?",
          "category": "unknown", "reply": ""}
result = builder.compile().invoke(ticket)
print(result["category"])
print(result["reply"])
