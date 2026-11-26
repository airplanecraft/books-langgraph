"""The fix: the model call gets a node of its own, before the node that asks.
Book: Chapter 7, section 7.4
Run: python ch07/fix_rerun.py
"""
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from common import ScriptedModel, say  # the stand-in model of chapter 0

model = ScriptedModel(script=[say("Draft one."), say("Draft two.")])


class State(TypedDict):
    draft: str


# region: fixed
def draft(state: State) -> dict:
    print("draft runs")  # ①
    return {"draft": model.invoke("Write a reply.").content}


def review(state: State) -> dict:
    print("review starts")
    interrupt({"question": "Send it?", "draft": state["draft"]})  # ②
    return {}


builder = StateGraph(State)
builder.add_node("draft", draft)
builder.add_node("review", review)
builder.add_edge(START, "draft")
builder.add_edge("draft", "review")
builder.add_edge("review", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
paused = graph.invoke({"draft": ""}, config)
print("shown to the person:", paused["__interrupt__"][0].value["draft"])
result = graph.invoke(Command(resume="approve"), config)
print("saved in the state:", result["draft"])  # ③
# endregion
