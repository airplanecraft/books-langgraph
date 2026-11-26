"""A node returns a Command and also has an edge: both targets run.
Book: Chapter 3, section 3.6
Run: python ch03/pitfall_both.py
"""
# region: both
from typing import Literal, TypedDict

from langgraph.errors import InvalidUpdateError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    reply: str


def classify(state: State) -> Command[Literal["billing_reply"]]:
    return Command(goto="billing_reply")  # ①


def billing_reply(state: State) -> dict:
    return {"reply": "billing"}


def general_reply(state: State) -> dict:
    return {"reply": "general"}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("billing_reply", billing_reply)
builder.add_node("general_reply", general_reply)
builder.add_edge(START, "classify")
builder.add_edge("classify", "general_reply")  # ②
builder.add_edge("billing_reply", END)
builder.add_edge("general_reply", END)
try:
    builder.compile().invoke({"reply": ""})
except InvalidUpdateError as error:
    print(str(error).splitlines()[0])  # ③
# endregion
