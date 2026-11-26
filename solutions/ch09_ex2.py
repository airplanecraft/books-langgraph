"""Exercise 9.2: a retry policy for ConnectionError only, and an error handler for everything else.
Book: Chapter 9, section 9.5
Run: python solutions/ch09_ex2.py
"""
import operator
from typing import Annotated, TypedDict

from langgraph.errors import NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, RetryPolicy


class State(TypedDict):
    notes: Annotated[list, operator.add]


def give_up(state: State, error: NodeError) -> Command:
    return Command(update={"notes": ["send failed"]}, goto="tell_human")


def tell_human(state: State) -> dict:
    return {"notes": ["a person will answer"]}


def attempts_for(error: Exception) -> int:
    attempts = []

    def send(state: State) -> dict:
        attempts.append("run")
        raise error

    policy = RetryPolicy(max_attempts=3, retry_on=ConnectionError,
                         initial_interval=0.01, jitter=False)
    builder = StateGraph(State)
    builder.add_node("send", send, retry_policy=policy, error_handler=give_up)
    builder.add_node("tell_human", tell_human)
    builder.add_edge(START, "send")
    builder.add_edge("tell_human", END)
    builder.compile().invoke({"notes": []})
    return len(attempts)


for error in (ConnectionError("down"), ValueError("bad address")):
    print(type(error).__name__, attempts_for(error))
