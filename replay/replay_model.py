"""A model that answers from the replies saved in a recording, so examples run offline.
Book: Chapter 0, section 0.6
Run: python -c "import replay.replay_model"  (used through common.get_model() when OFFLINE=1)
"""
import json
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage, messages_from_dict
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import ConfigDict, Field

REPLAY_DIR = Path(__file__).parent

# One tape per recording file: every model instance a script builds reads from the same one,
# in the order the real calls happened when the recording was made.
_TAPES: dict[Path, dict[str, Any]] = {}


class Cursor:
    """Position of the next reply; a plain object, so every model instance keeps pointing at the same one."""

    def __init__(self) -> None:
        self.position = 0


class ReplayModel(BaseChatModel):
    """Returns the saved model replies in order. It ignores what it is asked."""

    replies: list[BaseMessage]
    chunks: list[list[AIMessageChunk]] = []  # recorded stream chunks per reply; [] when none were recorded
    cursor: Cursor = Field(default_factory=Cursor)  # shared by every instance made from one recording
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_recording(cls, recording: Path) -> "ReplayModel":
        key = recording.resolve()
        if key not in _TAPES:
            steps = [step for step in json.loads(key.read_text())["steps"] if step["kind"] == "model"]
            replies = messages_from_dict([json.loads(step["text"]) for step in steps])
            chunks = [messages_from_dict(step.get("chunks", [])) for step in steps]
            _TAPES[key] = {"replies": replies, "chunks": chunks, "cursor": Cursor()}
        return cls(**_TAPES[key])

    @classmethod
    def for_script(cls, script: Path) -> "ReplayModel":
        recording = REPLAY_DIR / script.resolve().parent.name / f"{script.stem}.json"
        if not recording.exists():
            raise FileNotFoundError(f"No recording for {script.name}: expected {recording}")
        return cls.from_recording(recording)

    @staticmethod
    def forget_tapes() -> None:
        """Start every recording from its first reply again (tests that run scripts in one process)."""
        _TAPES.clear()

    @property
    def _llm_type(self) -> str:
        return "replay"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ReplayModel":
        return self

    def _next_index(self) -> int:
        index = self.cursor.position
        if index >= len(self.replies):
            raise RuntimeError("The recording has no replies left.")
        self.cursor.position = index + 1
        return index

    def _generate(self, messages: list[BaseMessage], stop: Any = None,
                  run_manager: Any = None, **kwargs: Any) -> ChatResult:
        return ChatResult(generations=[ChatGeneration(message=self.replies[self._next_index()])])

    def _chunks_for(self, index: int) -> list[AIMessageChunk]:
        if self.chunks[index]:
            return self.chunks[index]
        reply = self.replies[index]  # nothing recorded: the whole reply is one chunk
        return [AIMessageChunk(content=reply.content, id=reply.id, tool_call_chunks=[
            {"name": call["name"], "args": json.dumps(call["args"]), "id": call["id"], "index": number}
            for number, call in enumerate(getattr(reply, "tool_calls", []))],
            usage_metadata=getattr(reply, "usage_metadata", None),
            response_metadata=reply.response_metadata, additional_kwargs=reply.additional_kwargs)]

    def _stream(self, messages: list[BaseMessage], stop: Any = None,
                run_manager: Any = None, **kwargs: Any) -> Iterator[ChatGenerationChunk]:
        for chunk in self._chunks_for(self._next_index()):
            yield ChatGenerationChunk(message=chunk)

    async def _astream(self, messages: list[BaseMessage], stop: Any = None,
                       run_manager: Any = None, **kwargs: Any) -> AsyncIterator[ChatGenerationChunk]:
        for chunk in self._chunks_for(self._next_index()):
            yield ChatGenerationChunk(message=chunk)
