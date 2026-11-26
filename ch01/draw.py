"""List the nodes and edges of the graph and print it as Mermaid text.
Book: Chapter 1, section 1.5
Run: python ch01/draw.py
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


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", "draft")
builder.add_edge("draft", END)
graph = builder.compile()

# region: draw
drawing = graph.get_graph()  # ①
print(list(drawing.nodes))  # ②
print([(edge.source, edge.target) for edge in drawing.edges])  # ③
print(drawing.draw_mermaid())  # ④
# endregion
