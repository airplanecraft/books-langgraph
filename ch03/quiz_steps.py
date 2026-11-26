"""Self-check run: which super-step does the last node run in?
Book: Chapter 3, section 3.3
Run: python ch03/quiz_steps.py
"""
# region: steps
from typing import Literal, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    laps: int


def fetch(state: State) -> dict:
    return {"laps": state["laps"] + 1}


def check(state: State) -> dict:
    return {}


def after_check(state: State) -> Literal["fetch", "finish"]:
    return "finish" if state["laps"] >= 2 else "fetch"


def finish(state: State, config: RunnableConfig) -> dict:
    print("finish ran in super-step", config["metadata"]["langgraph_step"])
    return {}


builder = StateGraph(State)
builder.add_node("fetch", fetch)
builder.add_node("check", check)
builder.add_node("finish", finish)
builder.add_edge(START, "fetch")
builder.add_edge("fetch", "check")
builder.add_conditional_edges("check", after_check)
builder.add_edge("finish", END)
builder.compile().invoke({"laps": 0})
# endregion
