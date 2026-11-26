"""The waits between attempts: initial_interval, backoff_factor and max_interval.
Book: Chapter 9, section 9.4
Run: python ch09/backoff.py
"""
# region: server
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
# endregion


# region: waits
import operator
from typing import Annotated, TypedDict
from unittest.mock import patch

from langgraph.graph import START, StateGraph
from langgraph.types import RetryPolicy


class State(TypedDict):
    notes: Annotated[list, operator.add]


server = MailServer(failures=4)


def send(state: State) -> dict:
    return {"notes": [server.send()]}


policy = RetryPolicy(max_attempts=5, initial_interval=0.5,
                     backoff_factor=2.0, max_interval=1.5, jitter=False)
builder = StateGraph(State)
builder.add_node("send", send, retry_policy=policy)
builder.add_edge(START, "send")
graph = builder.compile()

waits: list = []
with patch("time.sleep", waits.append):  # ①
    result = graph.invoke({"notes": []})
print("attempts:", server.attempts)
print("waits asked for:", waits)  # ②
# endregion
