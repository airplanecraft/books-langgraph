"""A retry policy on a node: the node runs again after a ConnectionError.
Book: Chapter 9, section 9.3
Run: python ch09/retry.py
"""
# region: server
import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy


class State(TypedDict):
    notes: Annotated[list, operator.add]


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


# region: policy
def run(failures: int) -> None:
    server = MailServer(failures)

    def send(state: State) -> dict:
        return {"notes": [server.send()]}

    policy = RetryPolicy(max_attempts=3, initial_interval=0.01, jitter=False)
    builder = StateGraph(State)
    builder.add_node("send", send, retry_policy=policy)  # ①
    builder.add_edge(START, "send")
    builder.add_edge("send", END)
    graph = builder.compile()
    try:
        print("result:", graph.invoke({"notes": []})["notes"])
    except ConnectionError as error:  # ②
        print("invoke raised:", error)
    print("attempts:", server.attempts)  # ③


run(failures=2)
run(failures=5)
# endregion
