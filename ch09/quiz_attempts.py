"""Self-check run: how often a node runs under a retry policy with max_attempts=4.
Book: Chapter 9, section 9.3
Run: python ch09/quiz_attempts.py
"""
# region: quiz
import operator
from typing import Annotated, TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import RetryPolicy


class State(TypedDict):
    results: Annotated[list, operator.add]


calls = []


def lookup(state: State) -> dict:
    calls.append("run")
    if len(calls) <= 3:
        raise ConnectionError("database unreachable")
    return {"results": ["found it"]}


policy = RetryPolicy(max_attempts=4, initial_interval=0.01, jitter=False)
builder = StateGraph(State)
builder.add_node("lookup", lookup, retry_policy=policy)
builder.add_edge(START, "lookup")
result = builder.compile().invoke({"results": []})
print(len(calls), result["results"])
# endregion
