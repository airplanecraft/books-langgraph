"""The update of a Command goes through the reducer of its key.
Book: Chapter 3, section 3.5
Run: python ch03/command_reducer.py
"""
# region: reducer
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    notes: Annotated[list[str], operator.add]  # ①


def classify(state: State) -> Command[Literal["review"]]:
    return Command(update={"notes": ["classified"]}, goto="review")  # ②


def review(state: State) -> dict:
    return {"notes": ["reviewed"]}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("review", review)
builder.add_edge(START, "classify")
builder.add_edge("review", END)
result = builder.compile().invoke({"notes": ["received"]})
print(result["notes"])  # ③
# endregion
