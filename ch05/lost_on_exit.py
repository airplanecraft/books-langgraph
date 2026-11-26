"""An InMemorySaver lasts at most as long as its program: a second program starts empty.
Book: Chapter 5, section 5.6
Run: python ch05/lost_on_exit.py
"""
# region: exit
import subprocess
import sys
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str


def read(state: State) -> dict:
    return {}


def run_once() -> None:
    builder = StateGraph(State)
    builder.add_node("read", read)
    builder.add_edge(START, "read")
    builder.add_edge("read", END)
    graph = builder.compile(checkpointer=InMemorySaver())  # ①
    config = {"configurable": {"thread_id": "ana"}}
    before = len(list(graph.get_state_history(config)))
    graph.invoke({"customer": "Ana"}, config)
    after = len(list(graph.get_state_history(config)))
    print("checkpoints before:", before, "after:", after)


if sys.argv[1:] == ["child"]:  # ②
    run_once()
else:
    for number in (1, 2):
        command = [sys.executable, __file__, "child"]
        done = subprocess.run(command, capture_output=True, text=True)
        print("program", number, "-", done.stdout.strip())  # ③
# endregion
