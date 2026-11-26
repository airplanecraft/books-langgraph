"""Two Send mistakes: no reducer on the results key, and no list of destinations.
Book: Chapter 10, section 10.8
Run: python ch10/pitfall_send.py
"""
# region: pitfalls
from typing import TypedDict

from langgraph.errors import InvalidUpdateError
from langgraph.graph import START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send


class State(TypedDict):
    emails: list[str]
    results: list[str]  # ①


def fan_out(state: State) -> list[Send]:
    return [Send("classify", {"email": text}) for text in state["emails"]]


def classify(item: dict) -> dict:
    return {"results": [item["email"].upper()]}


def build(destinations: list[str] | None) -> CompiledStateGraph:
    builder = StateGraph(State)
    builder.add_node("classify", classify)
    builder.add_conditional_edges(START, fan_out, destinations)  # ②
    return builder.compile()


for emails in (["a"], ["a", "b"]):
    try:
        result = build(["classify"]).invoke({"emails": emails, "results": []})
        print(len(emails), result["results"])
    except InvalidUpdateError as error:
        print(len(emails), "InvalidUpdateError:", str(error).splitlines()[0])

for destinations in (["classify"], None):
    edges = build(destinations).get_graph().edges
    pairs = [(edge.source, edge.target) for edge in edges if edge.conditional]
    print(destinations, pairs)  # ③
# endregion
