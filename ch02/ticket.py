"""Put the chapter together: one ticket state with a rule for each key.
Book: Chapter 2, section 2.5
Run: python ch02/ticket.py
"""
# region: ticket
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


def keep_max(old: int, new: int) -> int:
    return max(old, new)


class State(TypedDict):
    customer: str  # no reducer: replace
    category: str  # no reducer: replace
    notes: Annotated[list[str], operator.add]  # ①
    urgency: Annotated[int, keep_max]  # ②


def read(state: State) -> dict:
    return {"category": "billing", "notes": ["read"], "urgency": 3}


def draft(state: State) -> dict:
    return {"notes": ["drafted"], "urgency": 2}


builder = StateGraph(State)
builder.add_node("read", read)
builder.add_node("draft", draft)
builder.add_edge(START, "read")
builder.add_edge("read", "draft")
builder.add_edge("draft", END)

start = {"customer": "Ana", "category": "unknown",
         "notes": ["received"], "urgency": 1}
for key, value in builder.compile().invoke(start).items():
    print(f"{key:9}", value)  # ③
# endregion
