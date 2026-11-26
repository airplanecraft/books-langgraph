"""Run two plain functions by hand, merging what each returns into the ticket.
Book: Chapter 1, section 1.2
Run: python ch01/plain_nodes.py
"""
# region: nodes
from typing import TypedDict


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def classify(state: State) -> dict:  # ①
    category = "billing" if "charged" in state["body"] else "other"
    return {"category": category}


def draft(state: State) -> dict:  # ②
    name, topic = state["customer"], state["category"]
    return {"reply": f"Hi {name}, we are checking your {topic} question."}


ticket: State = {"customer": "Ana", "body": "I was charged twice for May.",
                 "category": "unknown", "reply": ""}
slip = classify(ticket)  # ③
print("classify returned:", slip)
ticket.update(slip)  # ④
slip = draft(ticket)
print("draft returned:", slip)
ticket.update(slip)
print("final:")
for key, value in ticket.items():
    print(" ", key, "=", repr(value))
# endregion
