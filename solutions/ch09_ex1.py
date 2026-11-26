"""Exercise 9.1: the retry of Listing 9.6 with five attempts, for a server that fails four times.
Book: Chapter 9, section 9.3
Run: python solutions/ch09_ex1.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


class MailServer:
    """A toy mail server that fails its first `failures` calls."""

    def __init__(self, failures: int) -> None:
        self.failures = failures
        self.attempts = 0

    def send(self) -> str:
        self.attempts += 1
        if self.attempts <= self.failures:
            raise ConnectionError("mail server unreachable")
        return "sent the reply"


class State(TypedDict):
    notes: Annotated[list, operator.add]


server = MailServer(failures=4)


def send(state: State) -> dict:
    return {"notes": [server.send()]}


policy = RetryPolicy(max_attempts=5, initial_interval=0.01, jitter=False)
builder = StateGraph(State)
builder.add_node("send", send, retry_policy=policy)
builder.add_edge(START, "send")
builder.add_edge("send", END)
result = builder.compile().invoke({"notes": []})
print("result:", result["notes"])
print("attempts:", server.attempts)
