"""A loop: draft a reply, review it, and go back to drafting until it passes.
Book: Chapter 3, section 3.2
Run: python ch03/loop.py
"""
# region: nodes
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from common import ScriptedModel, say  # the helpers from chapter 0

replies = [say("Hi Ana, we got your email."),
           say("Sorry about the double charge. We will refund it.")]
model = ScriptedModel(script=replies)  # ①


class State(TypedDict):
    reply: str
    feedback: str
    approved: bool


def draft(state: State) -> dict:
    prompt = "Write a reply. " + state["feedback"]  # ②
    print("prompt:", prompt)
    message = {"role": "user", "content": prompt}
    reply = model.invoke([message]).content
    print("draft:", reply)
    return {"reply": reply}


def review(state: State) -> dict:
    approved = "refund" in state["reply"]  # ③
    print("review:", approved)
    feedback = "" if approved else "Mention the refund."
    return {"approved": approved, "feedback": feedback}


def after_review(state: State) -> Literal["draft", "__end__"]:  # ④
    return END if state["approved"] else "draft"
# endregion


# region: build
builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_node("review", review)
builder.add_edge(START, "draft")
builder.add_edge("draft", "review")
builder.add_conditional_edges("review", after_review)  # ①
graph = builder.compile()
graph.invoke({"reply": "", "feedback": "", "approved": False})
# endregion
