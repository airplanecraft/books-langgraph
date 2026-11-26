"""More tests for chapter 1: drawing, build errors, missing return, separate runs.
Book: Chapter 1, section 1.7
Run: python -m pytest tests/test_ch01_more.py
"""
from typing import TypedDict

import pytest
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    customer: str
    body: str
    category: str
    reply: str


def classify(state: State) -> dict:
    category = "billing" if "charged" in state["body"] else "other"
    return {"category": category}


def draft(state: State) -> dict:
    name, topic = state["customer"], state["category"]
    return {"reply": f"Hi {name}, we are checking your {topic} question."}


TICKET = {"customer": "Ana", "body": "I was charged twice for May.",
          "category": "unknown", "reply": ""}


def build() -> StateGraph:
    builder = StateGraph(State)
    builder.add_node("classify", classify)
    builder.add_node("draft", draft)
    builder.add_edge(START, "classify")
    builder.add_edge("classify", "draft")
    builder.add_edge("draft", END)
    return builder


def test_get_graph_lists_markers_nodes_and_edges() -> None:
    drawing = build().compile().get_graph()
    assert list(drawing.nodes) == ["__start__", "classify", "draft", "__end__"]
    assert [(e.source, e.target) for e in drawing.edges] == [
        ("__start__", "classify"), ("classify", "draft"), ("draft", "__end__")]
    assert "classify --> draft;" in drawing.draw_mermaid()


def test_draw_ascii_needs_a_package_that_is_not_installed() -> None:
    with pytest.raises(ImportError, match="grandalf"):
        build().compile().get_graph().draw_ascii()


def test_compile_names_an_unknown_node_in_an_edge() -> None:
    builder = StateGraph(State)
    builder.add_node("classify", classify)
    builder.add_edge(START, "clasify")
    with pytest.raises(ValueError, match="clasify"):
        builder.compile()


def test_compile_needs_an_edge_from_start() -> None:
    builder = StateGraph(State)
    builder.add_node("classify", classify)
    builder.add_edge("classify", END)
    with pytest.raises(ValueError, match="entrypoint"):
        builder.compile()
    with pytest.raises(AttributeError):
        builder.invoke(dict(TICKET))


def test_a_node_without_return_changes_nothing() -> None:
    def forgetful(state: State) -> None:
        category = "billing"  # noqa: F841

    builder = StateGraph(State)
    builder.add_node("classify", forgetful)
    builder.add_edge(START, "classify")
    builder.add_edge("classify", END)
    assert builder.compile().invoke(dict(TICKET))["category"] == "unknown"


def test_the_second_invoke_does_not_see_what_the_first_wrote() -> None:
    seen: list[dict] = []

    def classify_and_write(state: State) -> dict:
        seen.append(dict(state))
        return {"category": "billing", "reply": "Hi " + state["customer"]}

    builder = StateGraph(State)
    builder.add_node("classify", classify_and_write)
    builder.add_edge(START, "classify")
    builder.add_edge("classify", END)
    graph = builder.compile()
    graph.invoke({"customer": "Ana", "category": "unknown"})
    graph.invoke({"customer": "Ben", "category": "unknown"})
    assert seen[1] == {"customer": "Ben", "category": "unknown"}
