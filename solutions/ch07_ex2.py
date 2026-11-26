"""Exercise 7.2: a fourth answer, escalate, that goes to a node of its own.
Book: Chapter 7, section 7.6
Run: python solutions/ch07_ex2.py
"""
from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from common import ScriptedModel, say  # the helpers of chapter 0

model = ScriptedModel(script=[say("Hi Ana, B42 is delayed.")])


class State(TypedDict):
    customer: str
    email: str
    draft: str
    status: str


def draft_reply(state: State) -> dict:
    return {"draft": model.invoke(state["email"]).content}


def review(state: State) -> Command[Literal["send", "escalate", "__end__"]]:
    answer = interrupt({"question": "Send this reply?", "draft": state["draft"]})
    action = answer.get("action") if isinstance(answer, dict) else None
    if action == "approve":
        return Command(goto="send")
    if action == "edit":
        return Command(goto="send", update={"draft": answer["text"]})
    if action == "escalate":
        return Command(goto="escalate")
    return Command(goto=END, update={"status": "rejected"})


def send(state: State) -> dict:
    return {"status": "sent"}


def escalate(state: State) -> dict:
    return {"status": "escalated"}


builder = StateGraph(State)
builder.add_node("draft_reply", draft_reply)
builder.add_node("review", review)
builder.add_node("send", send)
builder.add_node("escalate", escalate)
builder.add_edge(START, "draft_reply")
builder.add_edge("draft_reply", "review")
builder.add_edge("send", END)
builder.add_edge("escalate", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "t5"}}
ticket = {"customer": "Ana", "email": "Where is my order B42?"}
graph.invoke(ticket, config)
result = graph.invoke(Command(resume={"action": "escalate"}), config)
print("t5 ->", result["status"], "|", result["draft"])
