"""A loop that never passes review stops at the recursion limit.
Book: Chapter 3, section 3.4
Run: python ch03/limit.py
"""
from typing import Literal, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from common import ScriptedModel, say


class State(TypedDict):
    reply: str
    feedback: str
    approved: bool


def draft(state: State, config: RunnableConfig) -> dict:
    step = config["metadata"]["langgraph_step"]
    print(f"super-step {step}: draft")
    prompt = "Write a reply. " + state["feedback"]
    reply = model.invoke([{"role": "user", "content": prompt}]).content
    return {"reply": reply}


# region: limit
from langgraph.errors import GraphRecursionError

model = ScriptedModel(script=[say("Hi Ana.")] * 3)


def review(state: State) -> dict:
    return {"approved": False, "feedback": ""}  # ①


def after_review(state: State) -> Literal["draft", "__end__"]:
    return END if state["approved"] else "draft"


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_node("review", review)
builder.add_edge(START, "draft")
builder.add_edge("draft", "review")
builder.add_conditional_edges("review", after_review)
graph = builder.compile()
start = {"reply": "", "feedback": "", "approved": False}
try:
    graph.invoke(start, config={"recursion_limit": 5})  # ②
except GraphRecursionError as error:
    print(str(error).splitlines()[0])  # ③
# endregion
