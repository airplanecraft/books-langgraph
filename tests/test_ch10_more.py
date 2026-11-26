"""More tests for chapter 10: facts that the chapter states or relies on.
Book: Chapter 10, section 10.8
Run: python -m pytest tests/test_ch10_more.py
"""
import operator
from typing import Annotated, TypedDict

import pytest
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.errors import GraphRecursionError, InvalidUpdateError
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class Log(TypedDict):
    log: Annotated[list[str], operator.add]


def node(label: str):
    def run(state: Log, config: RunnableConfig) -> dict:
        return {"log": [f"{label}@{config['metadata']['langgraph_step']}"]}

    return run


def fan(labels: list[str], defer: bool = False):
    builder = StateGraph(Log)
    builder.add_node("read", node("read"))
    builder.add_node("draft", node("draft"), defer=defer)
    builder.add_edge(START, "read")
    for label in labels:
        builder.add_node(label, node(label))
        builder.add_edge("read", label)
        builder.add_edge(label, "draft")
    builder.add_edge("draft", END)
    return builder.compile()


def test_updates_of_one_super_step_follow_the_node_names_as_text() -> None:
    log = fan(["b2", "b10", "B", "a"]).invoke({"log": []})["log"]
    assert log == ["read@1", "B@2", "a@2", "b10@2", "b2@2", "draft@3"]


def test_the_limit_is_the_number_of_super_steps_plus_one() -> None:
    graph = fan(["a", "b", "c", "d"])  # six node runs, three super-steps
    with pytest.raises(GraphRecursionError):
        graph.invoke({"log": []}, {"recursion_limit": 3})
    assert len(graph.invoke({"log": []}, {"recursion_limit": 4})["log"]) == 6


def test_two_equal_values_still_conflict() -> None:
    class Plain(TypedDict):
        note: str
    builder = StateGraph(Plain)
    for name in ("a", "b"):
        builder.add_node(name, lambda state: {"note": "same"})
        builder.add_edge(START, name)
        builder.add_edge(name, END)
    with pytest.raises(InvalidUpdateError):
        builder.compile().invoke({"note": ""})


class Items(TypedDict):
    items: list[str]
    results: Annotated[list[str], operator.add]
    summary: str


def send_graph():
    def fan_out(state: Items) -> list[Send]:
        return [Send("work", {"item": item}) for item in state["items"]]

    builder = StateGraph(Items)
    builder.add_node("work", lambda item: {"results": [item["item"]]})
    builder.add_node("done", lambda state: {"summary": "done"})
    builder.add_conditional_edges(START, fan_out, ["work"])
    builder.add_edge("work", "done")
    builder.add_edge("done", END)
    return builder.compile()


def test_send_results_keep_the_list_order_also_past_ten_items() -> None:
    items = [str(number) for number in (5, 3, 11, 0, 7, 1, 9, 2, 8, 4, 10, 6)]
    result = send_graph().invoke({"items": items, "results": [], "summary": ""})
    assert result["results"] == items
    assert result["summary"] == "done"


def test_an_empty_send_list_skips_the_node_after() -> None:
    result = send_graph().invoke({"items": [], "results": [], "summary": ""})
    assert result["summary"] == ""


def test_the_failed_branch_is_saved_with_its_error() -> None:
    state = {"up": False}
    def good(state_: Log) -> dict:
        return {"log": ["good"]}

    def flaky(state_: Log) -> dict:
        if not state["up"]:
            raise RuntimeError("down")
        return {"log": ["flaky"]}

    builder = StateGraph(Log)
    builder.add_node("good", good)
    builder.add_node("flaky", flaky)
    builder.add_edge(START, "good")
    builder.add_edge(START, "flaky")
    graph = builder.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "t"}}
    with pytest.raises(RuntimeError):
        graph.invoke({"log": []}, config)
    snapshot = graph.get_state(config)
    assert snapshot.next == ("flaky",)
    results = {task.name: task.result for task in snapshot.tasks}
    assert results == {"good": {"log": ["good"]}, "flaky": None}
    state["up"] = True
    assert graph.invoke(None, config) == {"log": ["flaky", "good"]}
