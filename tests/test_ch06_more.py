"""More tests for chapter 6: chunks, the writer outside a run, and stopping early.
Book: Chapter 6, section 6.6
Run: python -m pytest tests/test_ch06_more.py
"""
import json
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage

from ch06_helpers import QUESTION, State, agent, counting_graph
from replay.replay_model import ReplayModel

ROOT = Path(__file__).parent.parent


def test_the_stand_in_streams_each_reply_as_one_whole_message() -> None:
    items = list(agent().stream(QUESTION, stream_mode="messages"))
    assert [type(m) for m, _ in items] == [AIMessage, ToolMessage, AIMessage]
    assert [meta["langgraph_node"] for _, meta in items] == ["model", "tools", "model"]
    assert [meta["langgraph_step"] for _, meta in items] == [1, 2, 3]


def test_a_graph_without_a_model_streams_no_messages() -> None:
    assert list(counting_graph([True]).stream({"count": 0}, stream_mode="messages")) == []


def test_the_writer_outside_a_run_raises_runtime_error() -> None:
    from langgraph.config import get_stream_writer
    with pytest.raises(RuntimeError):
        get_stream_writer()


def test_stopping_the_loop_early_leaves_the_later_nodes_unrun() -> None:
    ran: list[str] = []
    graph = counting_graph([True, True])
    for _ in graph.stream({"count": 0}, stream_mode="updates"):
        ran.append("item")
        break
    assert ran == ["item"]


def test_the_recorded_chunks_add_up_to_the_recorded_reply() -> None:
    recording = ROOT / "replay" / "ch06" / "tokens.json"
    steps = [s for s in json.loads(recording.read_text())["steps"] if s["kind"] == "model"]
    for step in steps:
        reply = json.loads(step["text"])["data"]
        chunks = [AIMessageChunk(**c["data"] | {"type": "AIMessageChunk"}) for c in step["chunks"]]
        total = chunks[0]
        for chunk in chunks[1:]:
            total = total + chunk
        assert total.content == reply["content"]
        assert [(c["name"], c["args"]) for c in total.tool_calls] == \
               [(c["name"], c["args"]) for c in reply["tool_calls"]]


def test_the_replay_model_streams_the_recorded_chunks() -> None:
    ReplayModel.forget_tapes()
    model = ReplayModel.from_recording(ROOT / "replay" / "ch06" / "tokens.json")
    chunks = list(model.stream("hi"))
    steps = [s for s in json.loads((ROOT / "replay" / "ch06" / "tokens.json").read_text())["steps"]
             if s["kind"] == "model"]
    assert len(chunks) == len(steps[0]["chunks"])
    ReplayModel.forget_tapes()
