"""Starting from the newest copy: nothing is left to run.
Book: Chapter 8, section 8.7
Run: python ch08/pitfall_newest.py
"""
import operator
from typing import Annotated, Literal, TypedDict

from common import ScriptedModel, say  # the stand-in model of chapter 0

model = ScriptedModel(script=[say("Thanks for your email, we are on it.")])


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

config = {"configurable": {"thread_id": "ana"}}  # ②
ticket = {"email": "I was charged twice for order A17.", "notes": []}
result = graph.invoke(ticket, config)
print(result["category"], result["notes"])


history = list(graph.get_state_history(config))

# region: newest
newest = history[0]  # ①
print("next:", newest.next)
graph.invoke(None, newest.config)  # ②
copies = len(list(graph.get_state_history(config)))
print("copies:", len(history), "->", copies)
print("newest now:", graph.get_state(config).metadata["source"])
# endregion
