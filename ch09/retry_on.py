"""Which exceptions a retry policy retries, and what retry_on changes.
Book: Chapter 9, section 9.4
Run: python ch09/retry_on.py
"""
# region: kinds
from typing import TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import RetryPolicy


class State(TypedDict):
    notes: list


class MailboxFull(Exception):  # an error type of our own
    pass


def attempts_for(error_type: type, **policy_fields: object) -> int:
    attempts = []

    def send(state: State) -> dict:
        attempts.append("run")  # ①
        raise error_type("boom")

    policy = RetryPolicy(initial_interval=0.01, jitter=False, **policy_fields)
    builder = StateGraph(State)
    builder.add_node("send", send, retry_policy=policy)
    builder.add_edge(START, "send")
    try:
        builder.compile().invoke({"notes": []})
    except Exception:  # ②
        pass
    return len(attempts)


for error_type in (ConnectionError, TimeoutError, ValueError,
                   RuntimeError, MailboxFull):
    print(error_type.__name__, attempts_for(error_type))
print("ValueError with retry_on=ValueError:",
      attempts_for(ValueError, retry_on=ValueError))  # ③
print("ConnectionError with retry_on=ValueError:",
      attempts_for(ConnectionError, retry_on=ValueError))
# endregion
