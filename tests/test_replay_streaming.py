"""Checks that offline replay streams the recorded chunks: messages and updates mode, async, and a real recording.
Book: Chapter 0, section 0.6
Run: python -m pytest tests/test_replay_streaming.py
"""
import asyncio
import json
from pathlib import Path

from langchain_core.messages import AIMessage, AIMessageChunk

from replay_helpers import (ROOT, create_agent, TEXT_CHUNKS, TEXT_PIECES, TOOL_CALL, TOOL_CHUNKS, ReplayModel,  # noqa: F401
                            fresh_tapes, lookup_order, recording, write_recording)


def test_messages_mode_yields_the_recorded_chunks_in_order(recording: Path) -> None:
    agent = create_agent(ReplayModel.from_recording(recording), tools=[lookup_order])
    seen = [message for message, _ in agent.stream(
        {"messages": [("user", "Where is A17?")]}, stream_mode="messages") if isinstance(message, AIMessageChunk)]
    assert [chunk.content for chunk in seen] == [chunk.content for chunk in TOOL_CHUNKS + TEXT_CHUNKS]
    assert [chunk.tool_call_chunks for chunk in seen[:2]] == [chunk.tool_call_chunks for chunk in TOOL_CHUNKS[:2]]
    assert [chunk.content for chunk in seen if chunk.content] == TEXT_PIECES


def test_updates_mode_gets_the_message_assembled_from_the_chunks(recording: Path) -> None:
    agent = create_agent(ReplayModel.from_recording(recording), tools=[lookup_order])
    updates = list(agent.stream({"messages": [("user", "Where is A17?")]}, stream_mode="updates"))
    assert [list(update) for update in updates] == [["model"], ["tools"], ["model"]]
    assert updates[0]["model"]["messages"][0].tool_calls[0]["args"] == {"order_id": "A17"}
    assert updates[2]["model"]["messages"][0].content == "".join(TEXT_PIECES)


def test_without_recorded_chunks_each_reply_streams_as_one_chunk(tmp_path: Path) -> None:
    path = write_recording(tmp_path / "plain.json", [(AIMessage(content="Hello there.", id="run-c"), [])])
    chunks = list(ReplayModel.from_recording(path).stream("hi"))
    assert [chunk.content for chunk in chunks] == ["Hello there.", ""]


def test_without_recorded_chunks_a_tool_call_streams_as_one_chunk(tmp_path: Path) -> None:
    path = write_recording(tmp_path / "plain.json", [(AIMessage(content="", tool_calls=[TOOL_CALL], id="r"), [])])
    chunks = list(ReplayModel.from_recording(path).stream("hi"))
    merged = chunks[0]
    for chunk in chunks[1:]:
        merged = merged + chunk
    assert merged.tool_calls[0]["args"] == {"order_id": "A17"}


def test_async_stream_replays_the_recorded_chunks(recording: Path) -> None:
    import asyncio

    async def collect() -> list[str]:
        model = ReplayModel.from_recording(recording)
        return [chunk.content async for chunk in model.astream("hi")]

    assert asyncio.run(collect()) == [chunk.content for chunk in TOOL_CHUNKS]


def test_a_real_streamed_recording_replays_chunk_for_chunk() -> None:
    """tests/fixtures/real_stream_recording.json was recorded from the real model with lab/probes/streaming.py."""
    path = ROOT / "tests" / "fixtures" / "real_stream_recording.json"
    steps = [step for step in json.loads(path.read_text())["steps"] if step["kind"] == "model"]
    recorded = [chunk["data"]["content"] for step in steps for chunk in step["chunks"] if chunk["data"]["content"]]
    agent = create_agent(ReplayModel.from_recording(path), tools=[lookup_order])
    streamed = [message.content for message, _ in agent.stream(
        {"messages": [("user", "Where is order A17?")]}, stream_mode="messages")
        if isinstance(message, AIMessageChunk) and message.content]
    assert streamed == recorded
    assert len(recorded) > 5
