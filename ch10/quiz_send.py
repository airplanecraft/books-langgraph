"""Self-check run: Send objects over words of different lengths.
Book: Chapter 10, section 10.6
Run: python ch10/quiz_send.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class State(TypedDict):
    words: list[str]
    lengths: Annotated[list[int], operator.add]


def fan_out(state: State) -> list[Send]:
    return [Send("measure", {"word": word}) for word in state["words"]]


def measure(item: dict) -> dict:
    return {"lengths": [len(item["word"])]}


builder = StateGraph(State)
builder.add_node("measure", measure)
builder.add_conditional_edges(START, fan_out, ["measure"])
builder.add_edge("measure", END)
result = builder.compile().invoke({"words": ["ccc", "a", "bb"], "lengths": []})
print(sorted(result["lengths"]), sum(result["lengths"]))
