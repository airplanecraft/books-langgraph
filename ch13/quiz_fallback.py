"""Quiz run: three failures, three attempts, then the fallback node.
Book: Chapter 13, section 13.4
Run: python ch13/quiz_fallback.py
"""
from typing import TypedDict

from langgraph.errors import NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, RetryPolicy


class State(TypedDict):
    status: str


calls = []


def send(state: State) -> dict:
    calls.append("send")
    if len(calls) <= 3:
        raise ConnectionError("mail server unreachable")
    return {"status": "sent"}


def give_up(state: State, error: NodeError) -> Command:
    return Command(goto="to_person")


def to_person(state: State) -> dict:
    return {"status": "handed to a person"}


policy = RetryPolicy(initial_interval=0.01, jitter=False)
builder = StateGraph(State)
builder.add_node("send", send, retry_policy=policy, error_handler=give_up)
builder.add_node("to_person", to_person)
builder.add_edge(START, "send")
builder.add_edge("send", END)
builder.add_edge("to_person", END)
result = builder.compile().invoke({"status": ""})
print(result["status"], "|", len(calls), "attempts")
