"""Exercise 3.1: a third route, shipping, in the ticket graph of Listing 3.1.
Book: Chapter 3, section 3.1
Run: python solutions/ch03_ex1.py
"""
from typing import Literal, TypedDict

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


def route(state: State) -> Literal["billing_reply", "shipping_reply",
                                   "general_reply"]:
    if state["category"] == "billing":
        return "billing_reply"
    if state["category"] == "shipping":
        return "shipping_reply"
    return "general_reply"


def billing_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, we are checking the charge."}


def shipping_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, we are tracking your parcel."}


def general_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, thanks for your email."}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing_reply", billing_reply)
builder.add_node("shipping_reply", shipping_reply)
builder.add_node("general_reply", general_reply)
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route)
builder.add_edge("billing_reply", END)
builder.add_edge("shipping_reply", END)
builder.add_edge("general_reply", END)
graph = builder.compile()

emails = [
    {"customer": "Ana", "body": "I was charged twice for order B42."},
    {"customer": "Ben", "body": "Where is my parcel?"},
    {"customer": "Cy", "body": "Hello, do you have a phone number?"},
]
for email in emails:
    ticket = {**email, "category": "unknown", "reply": ""}
    result = graph.invoke(ticket)
    print(result["category"], "|", result["reply"])
