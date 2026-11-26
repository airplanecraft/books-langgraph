"""Exercise 5.1: the graph of Listing 5.4 with a third node, invoked twice on one thread.
Book: Chapter 5, section 5.3
Run: python solutions/ch05_ex1.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    notes: Annotated[list, operator.add]


def read(state: State) -> dict:
    return {"notes": ["read the email"]}


def draft(state: State) -> dict:
    return {"notes": ["wrote a reply"]}


def send(state: State) -> dict:
    return {"notes": ["sent the reply"]}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("draft", draft)
builder.add_edge(START, "read")
builder.add_edge("read", "draft")
builder.add_node("send", send)
builder.add_edge("draft", "send")
builder.add_edge("send", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
for _ in range(2):
    graph.invoke({"customer": "Ana", "notes": []}, config)
    print(len(list(graph.get_state_history(config))))
