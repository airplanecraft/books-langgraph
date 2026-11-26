"""Checks that every model instance of a script reads replies from one shared cursor.
Book: Chapter 0, section 0.6
Run: python -m pytest tests/test_replay_cursor.py
"""
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage
from langchain_core.tools import tool

from replay_helpers import (ROOT, create_agent, TEXT_PIECES, ReplayModel, fresh_tapes, recording,  # noqa: F401
                            write_recording)


def test_two_instances_share_one_cursor(recording: Path) -> None:
    main_model = ReplayModel.from_recording(recording)
    helper_model = ReplayModel.from_recording(recording)
    first = main_model.invoke("a")
    second = helper_model.invoke("b")
    assert first.tool_calls and second.content == "".join(TEXT_PIECES)
    with pytest.raises(RuntimeError, match="no replies left"):
        main_model.invoke("c")


def test_main_agent_and_subagent_each_take_the_next_reply(tmp_path: Path) -> None:
    sub_reply = AIMessage(content="A17 shipped", id="s")
    main_call = AIMessage(content="", tool_calls=[{"name": "ask_helper", "args": {"question": "A17?"},
                                                      "id": "call_9", "type": "tool_call"}], id="m1")
    main_final = AIMessage(content="Done.", id="m2")
    path = write_recording(tmp_path / "multi.json", [(main_call, []), (sub_reply, []), (main_final, [])])
    helper = create_agent(ReplayModel.from_recording(path), tools=[])

    @tool
    def ask_helper(question: str) -> str:
        """Ask the helper agent."""
        return helper.invoke({"messages": [("user", question)]})["messages"][-1].content

    main = create_agent(ReplayModel.from_recording(path), tools=[ask_helper])
    result = main.invoke({"messages": [("user", "go")]})
    assert [m.content for m in result["messages"]] == ["go", "", "A17 shipped", "Done."]


def test_for_script_instances_share_the_script_cursor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from replay import replay_model

    (tmp_path / "replay" / "ch00").mkdir(parents=True)
    write_recording(tmp_path / "replay" / "ch00" / "x.json", [(AIMessage(content="hi", id="a"), [])])
    monkeypatch.setattr(replay_model, "REPLAY_DIR", tmp_path / "replay")
    script = tmp_path / "ch00" / "x.py"
    first = ReplayModel.for_script(script)
    second = ReplayModel.for_script(script)
    assert first.cursor is second.cursor
    ReplayModel.forget_tapes()
    assert ReplayModel.for_script(script).cursor is not first.cursor
