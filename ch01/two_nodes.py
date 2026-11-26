"""Build and run a graph of two nodes: classify a ticket, then draft a reply.
Book: Chapter 1, section 1.3
Run: python ch01/two_nodes.py
"""
# region: graph
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


builder = StateGraph(State)  # ①
builder.add_node("draft", draft)  # ②
builder.add_node("classify", classify)
builder.add_edge(START, "classify")  # ③
builder.add_edge("classify", "draft")
builder.add_edge("draft", END)
graph = builder.compile()  # ④

ticket = {"customer": "Ana", "body": "I was charged twice for May.",
          "category": "unknown", "reply": ""}
result = graph.invoke(ticket)  # ⑤
print("final:")
for key, value in result.items():
    print(" ", key, "=", repr(value))
# endregion
