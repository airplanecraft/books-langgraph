"""Checks that a two-node StateGraph runs offline and that the recorder sees a model call made inside a node.
Book: Chapter 0, section 0.6
Run: python -m pytest tests/test_graph_smoke.py
"""
import importlib.util
import json
from pathlib import Path
from typing import TypedDict

import pytest
from langgraph.graph import END, START, StateGraph

from common import ScriptedModel, ask_for, say
from replay_helpers import ROOT, ReplayModel, fresh_tapes, write_recording  # noqa: F401

LAB = ROOT.parent / "lab" / "record.py"


class State(TypedDict):
    question: str
    answer: str


def build(model) -> object:
    def clean(state: State) -> dict:
        return {"question": state["question"].strip()}

    def ask(state: State) -> dict:
        return {"answer": model.invoke(state["question"]).content}

    graph = StateGraph(State)
    graph.add_node("clean", clean)
    graph.add_node("ask", ask)
    graph.add_edge(START, "clean")
    graph.add_edge("clean", "ask")
    graph.add_edge("ask", END)
    return graph.compile()


def test_two_node_graph_runs_with_the_scripted_model() -> None:
    result = build(ScriptedModel(script=[say("shipped")])).invoke({"question": "  Where is A17?  "})
    assert result == {"question": "Where is A17?", "answer": "shipped"}


def test_ask_for_builds_a_tool_call_reply() -> None:
    reply = ask_for("lookup_order", {"order_id": "A17"})
    assert reply.tool_calls[0]["name"] == "lookup_order"


def test_two_node_graph_runs_with_the_replay_model(tmp_path: Path) -> None:
    from langchain_core.messages import AIMessage

    path = write_recording(tmp_path / "g.json", [(AIMessage(content="shipped", id="r"), [])])
    assert build(ReplayModel.from_recording(path)).invoke({"question": "q"})["answer"] == "shipped"


@pytest.mark.skipif(not LAB.exists(), reason="lab/ is not part of the public repository")
def test_the_recorder_sees_a_model_call_made_inside_a_node(tmp_path: Path) -> None:
    from langchain_core.messages import AIMessage

    spec = importlib.util.spec_from_file_location("record_under_test", LAB)
    record = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(record)
    record.USAGE = tmp_path / "usage.jsonl"
    source = write_recording(tmp_path / "g.json", [(AIMessage(content="shipped", id="r"), [])])
    recorder = record.Recorder("00-test", "ch00/x.py")
    model = ReplayModel.from_recording(source)
    model.callbacks = [recorder]
    assert build(model).invoke({"question": "q"})["answer"] == "shipped"
    assert [json.loads(step["text"])["data"]["content"] for step in recorder.model_steps()] == ["shipped"]
