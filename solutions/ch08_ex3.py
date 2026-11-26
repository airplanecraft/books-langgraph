"""Exercise 8.3: a helper that finds the copy before a node, for a fork and a rerun.
Book: Chapter 8, section 8.5
Run: python solutions/ch08_ex3.py
"""
import operator
from typing import Annotated, Literal, TypedDict

from common import ScriptedModel, say  # the stand-in model of chapter 0

replies = [say("Thanks, we are on it."), say("Thanks again.")]
model = ScriptedModel(script=replies)


class State(TypedDict):
    email: str
    category: str
    notes: Annotated[list, operator.add]
    reply: str


def classify(state: State) -> dict:
    found = "refund" in state["email"].lower()  # ①
    return {"category": "billing" if found else "general",
            "notes": ["classified"]}


def route(state: State) -> Literal["draft", "escalate"]:
    return "escalate" if state["category"] == "billing" else "draft"


def draft(state: State) -> dict:
    print("draft runs")
    prompt = f"Reply in two sentences to: {state['email']}"
    reply = model.invoke(prompt).content  # ②
    return {"reply": reply, "notes": ["drafted"]}


def send(state: State) -> dict:
    print("SENT")  # stands for the mail service
    return {"notes": ["sent"]}


def escalate(state: State) -> dict:
    print("ESCALATED")  # hands the ticket to a person
    return {"notes": ["passed to a person"]}

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("draft", draft)
builder.add_node("send", send)
builder.add_node("escalate", escalate)
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route)  # ①
builder.add_edge("draft", "send")
builder.add_edge("send", END)
builder.add_edge("escalate", END)
graph = builder.compile(checkpointer=InMemorySaver())



def copy_before(graph: CompiledStateGraph, config: dict, node: str) -> dict:
    """The config of the newest copy of the thread that waits for `node`."""
    for snapshot in graph.get_state_history(config):
        if snapshot.next == (node,):
            return snapshot.config
    raise ValueError(f"no copy waits for {node}")


config = {"configurable": {"thread_id": "ana"}}
ticket = {"email": "I was charged twice for order A17.", "notes": []}
graph.invoke(ticket, config)
fork = graph.update_state(copy_before(graph, config, "draft"),
                          {"category": "billing"})
result = graph.invoke(None, fork)
print(result["category"], result["notes"])
result = graph.invoke(None, copy_before(graph, config, "classify"))
print(result["category"], result["notes"])
print("copies", len(list(graph.get_state_history(config))))
