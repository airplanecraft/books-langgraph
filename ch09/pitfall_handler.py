"""Two mistakes with an error handler: no goto, and a parameter with the wrong name.
Book: Chapter 9, section 9.7
Run: python ch09/pitfall_handler.py
"""
# region: handler
import operator
from typing import Annotated, TypedDict

from langgraph.errors import NodeError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    notes: Annotated[list, operator.add]


def send(state: State) -> dict:
    raise ConnectionError("mail server unreachable")


def no_goto(state: State, error: NodeError) -> Command:
    return Command(update={"notes": ["send failed"]})  # ①


def wrong_name(state: State, err: NodeError) -> Command:  # ②
    return Command(update={"notes": ["send failed"]})


def run(handler: object) -> None:
    builder = StateGraph(State)
    builder.add_node("send", send, error_handler=handler)
    builder.add_node("close", lambda state: {"notes": ["closed"]})
    builder.add_edge(START, "send")
    builder.add_edge("send", "close")
    builder.add_edge("close", END)
    try:
        graph = builder.compile()
        print(graph.invoke({"notes": ["read the email"]})["notes"])
    except TypeError as error:  # ③
        print("TypeError:", error)


run(no_goto)
run(wrong_name)
# endregion
