"""An error handler routes the card elsewhere once the retries run out.
Book: Chapter 9, section 9.5
Run: python ch09/error_handler.py
"""
# region: handler
import operator
from typing import Annotated, TypedDict

from langgraph.errors import NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, RetryPolicy

attempts: list = []


class State(TypedDict):
    notes: Annotated[list, operator.add]


def send(state: State) -> dict:
    attempts.append("run")
    raise ConnectionError("mail server unreachable")


def give_up(state: State, error: NodeError) -> Command:  # ①
    note = f"{error.node} failed: {error.error}"
    return Command(update={"notes": [note]}, goto="tell_human")  # ②


def tell_human(state: State) -> dict:
    return {"notes": ["a person will answer the customer"]}


policy = RetryPolicy(initial_interval=0.01, jitter=False)
builder = StateGraph(State)
builder.add_node("send", send, retry_policy=policy,
                 error_handler=give_up)  # ③
builder.add_node("tell_human", tell_human)
builder.add_edge(START, "send")
builder.add_edge("tell_human", END)
result = builder.compile().invoke({"notes": ["read the email"]})
print("attempts:", len(attempts))
for note in result["notes"]:
    print("note:", note)
# endregion
