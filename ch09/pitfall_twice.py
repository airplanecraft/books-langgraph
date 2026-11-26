"""A retry runs the whole node again, so a mail can go out twice.
Book: Chapter 9, section 9.7
Run: python ch09/pitfall_twice.py
"""
# region: twice
from typing import TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import RetryPolicy


class LossyMailServer:
    """A toy mail server that sends the mail, then loses the first reply."""

    def __init__(self) -> None:
        self.sent: dict = {}
        self.calls = 0

    def send(self, text: str, key: str = "") -> None:
        self.calls += 1
        self.sent[key or f"call {self.calls}"] = text  # ①
        if self.calls == 1:
            raise ConnectionError("the reply was lost")


class State(TypedDict):
    customer: str


def run(key: str) -> None:
    server = LossyMailServer()

    def send(state: State) -> dict:
        server.send("Your refund is on its way.", key)  # ②
        return {}
    policy = RetryPolicy(initial_interval=0.01, jitter=False)
    builder = StateGraph(State)
    builder.add_node("send", send, retry_policy=policy)
    builder.add_edge(START, "send")
    builder.compile().invoke({"customer": "Ana"})
    print(f"key={key!r}: calls={server.calls} mails={len(server.sent)}")


run("")
run("ticket-17")  # ③
# endregion
