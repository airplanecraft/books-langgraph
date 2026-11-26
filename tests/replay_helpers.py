"""Shared pieces of the replay tests: a tiny tool, recorded-chunk fixtures and a recording writer.
Book: Chapter 0, section 0.6
Run: python -m pytest   (imported by test_replay_streaming.py and test_replay_cursor.py)
"""
import json
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk, message_to_dict
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from replay.replay_model import ReplayModel  # noqa: E402


@tool
def lookup_order(order_id: str) -> str:
    """Look up the status of a customer order."""
    return "shipped"


def create_agent(model, tools: list):
    """A model node, a ToolNode and a conditional edge, built by hand (test helper only, not part of the book)."""
    bound = model.bind_tools(tools) if tools else model

    def call_model(state: MessagesState) -> dict:
        return {"messages": [bound.invoke(state["messages"])]}

    graph = StateGraph(MessagesState)
    graph.add_node("model", call_model)
    graph.add_edge(START, "model")
    if tools:
        graph.add_node("tools", ToolNode(tools))
        graph.add_conditional_edges("model", tools_condition)
        graph.add_edge("tools", "model")
    else:
        graph.add_edge("model", END)
    return graph.compile()


def dump(message) -> dict:
    return json.loads(json.dumps(message_to_dict(message)))


def write_recording(path: Path, replies: list[tuple[AIMessage, list[AIMessageChunk]]]) -> Path:
    steps = [{"kind": "code", "text": "x"}]
    for reply, chunks in replies:
        step = {"kind": "model", "text": json.dumps(dump(reply))}
        if chunks:
            step["chunks"] = [dump(chunk) for chunk in chunks]
        steps.append(step)
    path.write_text(json.dumps({"version": 1, "steps": steps}))
    return path


TOOL_CALL = {"name": "lookup_order", "args": {"order_id": "A17"}, "id": "call_1", "type": "tool_call"}
TOOL_CHUNKS = [
    AIMessageChunk(content="", id="run-a", tool_call_chunks=[
        {"name": "lookup_order", "args": '{"order_id": ', "id": "call_1", "index": 0}]),
    AIMessageChunk(content="", id="run-a", tool_call_chunks=[
        {"name": None, "args": '"A17"}', "id": None, "index": 0}]),
    AIMessageChunk(content="", id="run-a", chunk_position="last"),
]
TEXT_PIECES = ["Order ", "A17 ", "has ", "shipped."]
TEXT_CHUNKS = [AIMessageChunk(content=piece, id="run-b") for piece in TEXT_PIECES]
TEXT_CHUNKS.append(AIMessageChunk(content="", id="run-b", chunk_position="last"))


@pytest.fixture(autouse=True)
def fresh_tapes() -> None:
    ReplayModel.forget_tapes()


@pytest.fixture
def recording(tmp_path: Path) -> Path:
    return write_recording(tmp_path / "agent.json", [
        (AIMessage(content="", tool_calls=[TOOL_CALL], id="run-a"), TOOL_CHUNKS),
        (AIMessage(content="".join(TEXT_PIECES), id="run-b"), TEXT_CHUNKS),
    ])
