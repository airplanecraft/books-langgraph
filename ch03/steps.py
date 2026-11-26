"""Each node run in the draft and review loop is one super-step.
Book: Chapter 3, section 3.3
Run: python ch03/steps.py
"""
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from common import ScriptedModel, say

replies = [say("Hi Ana, we got your email."),
           say("Sorry about the double charge. We will refund it.")]
model = ScriptedModel(script=replies)


class State(TypedDict):
    reply: str
    feedback: str
    approved: bool


# region: steps
from langchain_core.runnables import RunnableConfig


def draft(state: State, config: RunnableConfig) -> dict:
    step = config["metadata"]["langgraph_step"]  # ①
    print(f"super-step {step}: draft")
    prompt = "Write a reply. " + state["feedback"]
    reply = model.invoke([{"role": "user", "content": prompt}]).content
    return {"reply": reply}


def review(state: State, config: RunnableConfig) -> dict:
    step = config["metadata"]["langgraph_step"]
    print(f"super-step {step}: review")
    approved = "refund" in state["reply"]
    feedback = "" if approved else "Mention the refund."
    return {"approved": approved, "feedback": feedback}
# endregion


def after_review(state: State) -> Literal["draft", "__end__"]:
    return END if state["approved"] else "draft"


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_node("review", review)
builder.add_edge(START, "draft")
builder.add_edge("draft", "review")
builder.add_conditional_edges("review", after_review)
graph = builder.compile()
graph.invoke({"reply": "", "feedback": "", "approved": False})
