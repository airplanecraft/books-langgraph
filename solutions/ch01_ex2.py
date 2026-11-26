"""Exercise 1.2: add a third node, sign, after draft.
Book: Chapter 1, section 1.4
Run: python solutions/ch01_ex2.py
"""
from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def classify(state: State) -> dict:
    category = "billing" if "charged" in state["body"] else "other"
    return {"category": category}


def draft(state: State) -> dict:
    name, topic = state["customer"], state["category"]
    return {"reply": f"Hi {name}, we are checking your {topic} question."}


def sign(state: State) -> dict:
    return {"reply": state["reply"] + " -- Support team"}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("draft", draft)
builder.add_node("sign", sign)
builder.add_edge(START, "classify")
builder.add_edge("classify", "draft")
builder.add_edge("draft", "sign")
builder.add_edge("sign", END)

ticket = {"customer": "Ana", "body": "I was charged twice for May.",
          "category": "unknown", "reply": ""}
print(builder.compile().invoke(ticket)["reply"])
