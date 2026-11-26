"""A Send object per email: one classify run each, with its own input.
Book: Chapter 10, section 10.6
Run: python ch10/send_map.py
"""
# region: send
import operator
from typing import Annotated, TypedDict

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class State(TypedDict):
    emails: list[str]
    results: Annotated[list[str], operator.add]  # ①
    summary: str


def fan_out(state: State) -> list[Send]:
    return [Send("classify", {"email": body})
            for body in state["emails"]]  # ②


def classify(item: dict, config: RunnableConfig) -> dict:  # ③
    number = config["metadata"]["langgraph_step"]
    category = "billing" if "charged" in item["email"] else "other"
    return {"results": [f"{category}, super-step {number}, got {item}"]}


def summarize(state: State) -> dict:
    return {"summary": f"{len(state['results'])} classified"}


builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("summarize", summarize)
builder.add_conditional_edges(START, fan_out, ["classify"])  # ④
builder.add_edge("classify", "summarize")
builder.add_edge("summarize", END)
graph = builder.compile()
# endregion

# region: run
inbox = ["Cy: I was charged twice", "Ana: parcel is late", "Ben: no invoice"]
for emails in (inbox, inbox[:1], []):
    result = graph.invoke({"emails": emails, "results": [], "summary": ""})
    print("emails:", len(emails), "|", result["summary"] or "(no summary)")
    for line in result["results"]:
        print("  ", line)
# endregion
