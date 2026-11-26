"""Shared helpers: the chat model, a scripted stand-in model, offline replay.
Book: Chapter 0, section 0.6
Run: python -c "import common"  (chapter scripts import it)
"""
# region: get_model
import os
import sys
from pathlib import Path

from langchain_core.language_models.chat_models import BaseChatModel

ROOT = Path(__file__).parent
MODEL_NAME = "deepseek-flash"


def load_env() -> None:
    """Read KEY=value lines from .env into the environment."""
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key.strip(), value)


def get_model() -> BaseChatModel:
    """The real DeepSeek model, or this script's saved replies (OFFLINE=1)."""
    if os.environ.get("OFFLINE") == "1":
        from replay.replay_model import ReplayModel

        return ReplayModel.for_script(Path(sys.argv[0]))
    load_env()
    if not os.environ.get("DEEPSEEK_API_KEY"):
        sys.exit("No DEEPSEEK_API_KEY. Put it in .env, or run with OFFLINE=1.")
    from langchain_deepseek import ChatDeepSeek

    return ChatDeepSeek(model=MODEL_NAME, temperature=0)
# endregion


# region: scripted_replies
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage


def say(text: str) -> AIMessage:
    """A scripted reply with no tool call."""
    return AIMessage(content=text)


def ask_for(tool_name: str, arguments: dict[str, Any],
            call_id: str = "call_1") -> AIMessage:
    """A scripted reply that asks for one tool call (and has no text)."""
    call = {"name": tool_name, "args": arguments, "id": call_id}
    return AIMessage(content="", tool_calls=[call])
# endregion


# region: scripted_model
from langchain_core.outputs import ChatGeneration, ChatResult


class ScriptedModel(BaseChatModel):
    """A stand-in model: scripted replies, no network; notes tools offered."""

    script: list[BaseMessage]
    tools_offered: list[str] = []
    replies_used: int = 0  # read by position; the caller's list stays intact

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedModel":
        names = []
        for tool in tools:
            if isinstance(tool, dict):
                names.append(tool["name"])
            else:
                names.append(getattr(tool, "name", str(tool)))
        self.tools_offered = names
        return self

    def _generate(self, messages: list[BaseMessage], stop: Any = None,
                  run_manager: Any = None, **kwargs: Any) -> ChatResult:
        if self.replies_used >= len(self.script):
            raise RuntimeError("The scripted model has no replies left.")
        reply = self.script[self.replies_used]
        self.replies_used += 1
        return ChatResult(generations=[ChatGeneration(message=reply)])
# endregion
