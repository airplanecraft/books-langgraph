"""Without a Literal return type the drawn graph has no conditional edges.
Book: Chapter 3, section 3.6
Run: python ch03/pitfall_draw.py
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


# region: plain
def route(state: State):  # ①
    if state["category"] == "billing":
        return "billing_reply"
    return "general_reply"
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
edges = graph.get_graph().edges
print([(e.source, e.target) for e in edges if e.conditional])
