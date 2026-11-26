"""The node starts again on resume: a draft made before interrupt is made twice.
Book: Chapter 7, section 7.4
Run: python ch07/pitfall_rerun.py
"""
# region: rerun
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from common import ScriptedModel, say  # the stand-in model of chapter 0

model = ScriptedModel(script=[say("Draft one."), say("Draft two.")])


class State(TypedDict):
    draft: str


def look_up(state: State) -> dict:
    print("look_up runs")  # ①
    return {}


def review(state: State) -> dict:
    print("review starts")  # ②
    draft = model.invoke("Write a reply.").content  # ③
    interrupt({"question": "Send it?", "draft": draft})
    return {"draft": draft}


builder = StateGraph(State)
builder.add_node("look_up", look_up)
builder.add_node("review", review)
builder.add_edge(START, "look_up")
builder.add_edge("look_up", "review")
builder.add_edge("review", END)
graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "ana"}}
paused = graph.invoke({"draft": ""}, config)
print("shown to the person:", paused["__interrupt__"][0].value["draft"])
result = graph.invoke(Command(resume="approve"), config)
print("saved in the state:", result["draft"])  # ④
# endregion
