"""The model classifies the email; a conditional edge reads its answer.
Book: Chapter 3, section 3.1
Run: python ch03/route_model.py   (or OFFLINE=1 python ch03/route_model.py)
"""
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


# region: classify
from common import get_model  # the helper from chapter 0

model = get_model()


def classify(state: State) -> dict:
    question = ("Is this email about billing or about something else? "
                "Answer with one word, billing or other.\n\n" + state["body"])
    answer = model.invoke([{"role": "user", "content": question}])  # ①
    category = "billing" if "billing" in answer.content.lower() else "other"
    return {"category": category}  # ②
# endregion


def route(state: State) -> Literal["billing_reply", "general_reply"]:
    if state["category"] == "billing":
        return "billing_reply"
    return "general_reply"


def billing_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, we are checking the charge."}


def general_reply(state: State) -> dict:
    return {"reply": f"Hi {state['customer']}, thanks for your email."}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing_reply", billing_reply)
builder.add_node("general_reply", general_reply)
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route)
builder.add_edge("billing_reply", END)
builder.add_edge("general_reply", END)
graph = builder.compile()

emails = [
    {"customer": "Ana", "body": "I was charged twice for order B42."},
    {"customer": "Ben", "body": "Where is my parcel?"},
]
for email in emails:
    ticket = {**email, "category": "unknown", "reply": ""}
    result = graph.invoke(ticket)
    print(result["category"], "|", result["reply"])
