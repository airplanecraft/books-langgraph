"""Checks replay across interrupt/resume (one cursor keeps reading) and across time travel (a re-run calls the model again).
Book: Chapter 7, section 7.2
Run: python -m pytest tests/test_replay_resume_timetravel.py
"""
from pathlib import Path
from typing import TypedDict

import pytest
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from replay_helpers import ReplayModel, fresh_tapes, write_recording  # noqa: F401


class State(TypedDict):
    draft: str
    decision: str
    final: str


def recording_of(tmp_path: Path, *texts: str) -> Path:
    return write_recording(tmp_path / "r.json", [(AIMessage(content=text, id=f"m{n}"), []) for n, text in enumerate(texts)])


def build_review(model, calls: list[str]):
    """draft (model) -> approve (interrupt only) -> finish (model)."""
    def draft(state: State) -> dict:
        calls.append("draft")
        return {"draft": model.invoke("write").content}

    def approve(state: State) -> dict:
        return {"decision": interrupt({"draft": state["draft"]})}

    def finish(state: State) -> dict:
        calls.append("finish")
        return {"final": model.invoke(f"polish: {state['decision']}").content}

    graph = StateGraph(State)
    for name, node in (("draft", draft), ("approve", approve), ("finish", finish)):
        graph.add_node(name, node)
    graph.add_edge(START, "draft")
    graph.add_edge("draft", "approve")
    graph.add_edge("approve", "finish")
    graph.add_edge("finish", END)
    return graph.compile(checkpointer=InMemorySaver())


def test_resume_continues_the_same_replay_cursor(tmp_path: Path) -> None:
    model = ReplayModel.from_recording(recording_of(tmp_path, "first draft", "polished"))
    calls: list[str] = []
    graph = build_review(model, calls)
    config = {"configurable": {"thread_id": "t1"}}
    paused = graph.invoke({}, config)
    assert paused["__interrupt__"][0].value == {"draft": "first draft"}
    assert model.cursor.position == 1
    done = graph.invoke(Command(resume="ok"), config)
    assert done["final"] == "polished" and done["draft"] == "first draft"
    assert calls == ["draft", "finish"]  # the draft node did not run again on resume
    assert model.cursor.position == 2


def test_model_inside_the_interrupt_node_is_called_again_on_resume(tmp_path: Path) -> None:
    """Why outline rule 1 exists: the node runs from its start on resume, so a model call before interrupt() reads a second reply."""
    model = ReplayModel.from_recording(recording_of(tmp_path, "one", "two", "three"))

    def risky(state: State) -> dict:
        draft = model.invoke("write").content
        return {"draft": draft, "decision": interrupt(draft)}

    graph = StateGraph(State)
    graph.add_node("risky", risky)
    graph.add_edge(START, "risky")
    graph.add_edge("risky", END)
    compiled = graph.compile(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": "t3"}}
    compiled.invoke({}, config)
    result = compiled.invoke(Command(resume="ok"), config)
    assert result["draft"] == "two"  # not "one": the book's output would drift
    assert model.cursor.position == 2


def test_time_travel_rerun_reads_the_extra_reply_in_order(tmp_path: Path) -> None:
    model = ReplayModel.from_recording(recording_of(tmp_path, "draft A", "final A", "final B"))
    calls: list[str] = []
    graph = build_review(model, calls)
    config = {"configurable": {"thread_id": "t4"}}
    graph.invoke({}, config)
    assert graph.invoke(Command(resume="ok"), config)["final"] == "final A"
    before_finish = next(s for s in graph.get_state_history(config) if s.next == ("finish",))
    assert before_finish.values["draft"] == "draft A"
    rerun = graph.invoke(None, before_finish.config)
    assert rerun["final"] == "final B"  # the model was called again: third reply in the recording
    assert calls == ["draft", "finish", "finish"]
    assert model.cursor.position == 3


def test_fork_with_update_state_then_rerun_reads_next_reply(tmp_path: Path) -> None:
    model = ReplayModel.from_recording(recording_of(tmp_path, "draft A", "final A", "final B"))
    graph = build_review(model, [])
    config = {"configurable": {"thread_id": "t5"}}
    graph.invoke({}, config)
    graph.invoke(Command(resume="ok"), config)
    before_finish = next(s for s in graph.get_state_history(config) if s.next == ("finish",))
    fork = graph.update_state(before_finish.config, {"decision": "edited"})
    assert graph.invoke(None, fork)["final"] == "final B"


def test_time_travel_beyond_the_recording_fails_clearly(tmp_path: Path) -> None:
    model = ReplayModel.from_recording(recording_of(tmp_path, "draft A", "final A"))
    graph = build_review(model, [])
    config = {"configurable": {"thread_id": "t6"}}
    graph.invoke({}, config)
    graph.invoke(Command(resume="ok"), config)
    before_finish = next(s for s in graph.get_state_history(config) if s.next == ("finish",))
    with pytest.raises(RuntimeError, match="no replies left"):
        graph.invoke(None, before_finish.config)
