"""A plain invoke on a paused thread starts a new run; a resume on another thread starts one too.
Book: Chapter 7, section 7.9
Run: python ch07/pitfall_resume.py
"""
# region: wrong
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    status: str


def look_up(state: State) -> dict:
    print("look_up runs")
    return {}


def review(state: State) -> dict:
    print("review starts")
    return {"status": interrupt("Send this reply?")}


builder = StateGraph(State)
builder.add_node("look_up", look_up)
builder.add_node("review", review)
builder.add_edge(START, "look_up")
builder.add_edge("look_up", "review")
builder.add_edge("review", END)
graph = builder.compile(checkpointer=InMemorySaver())
ana = {"configurable": {"thread_id": "ana"}}
ben = {"configurable": {"thread_id": "ben"}}
graph.invoke({"status": "new"}, ana)
again = graph.invoke({"status": "new"}, ana)  # ①
print("plain invoke on ana:", again["__interrupt__"][0].value)
graph.invoke(Command(resume="approve"), ben)  # ②
try:
    graph.invoke(Command(resume=None), ben)  # ③
except UnboundLocalError as error:
    print("resume=None:", type(error).__name__, graph.get_state(ben).next)
other = {"configurable": {"thread_id": "ana"}}  # ④
print("other code:", graph.invoke(Command(resume="yes"), other)["status"])
# endregion
