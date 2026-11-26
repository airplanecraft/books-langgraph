"""A graph whose second node asks the chat model to write the reply.
Book: Chapter 1, section 1.6
Run: python ch01/model_node.py   (or OFFLINE=1 python ch01/model_node.py)
"""
# region: ask
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from common import get_model  # the helper from chapter 0

model = get_model()


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def classify(state: State) -> dict:
    category = "billing" if "charged" in state["body"] else "other"
    return {"category": category}


def draft(state: State) -> dict:
    prompt = (f"Write a one-sentence reply to {state['customer']}, who wrote "
              f"about {state['category']}: {state['body']}")
    answer = model.invoke([{"role": "user", "content": prompt}])  # ①
    return {"reply": answer.content}  # ②


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("draft", draft)
builder.add_edge(START, "classify")
builder.add_edge("classify", "draft")
builder.add_edge("draft", END)
graph = builder.compile()

ticket = {"customer": "Ana", "body": "I was charged twice for May.",
          "category": "unknown", "reply": ""}
print(graph.invoke(ticket)["reply"])  # ③
# endregion
