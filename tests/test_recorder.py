"""Checks that the recorder keeps replies in the order the calls started and stores streamed chunks.
Book: Chapter 0, section 0.6
Run: python -m pytest tests/test_recorder.py   (skipped in the public repository, which has no lab/)
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage, AIMessageChunk

ROOT = Path(__file__).parent.parent
LAB = ROOT.parent / "lab" / "record.py"
sys.path.insert(0, str(ROOT))

from replay.replay_model import ReplayModel  # noqa: E402
from tests.replay_helpers import TEXT_CHUNKS, TEXT_PIECES, write_recording  # noqa: E402

pytestmark = pytest.mark.skipif(not LAB.exists(), reason="lab/ is not part of the public repository")


def load_recorder():
    spec = importlib.util.spec_from_file_location("record_under_test", LAB)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.USAGE = ROOT / "tests" / "_usage_unused.jsonl"
    return module


@pytest.fixture(autouse=True)
def no_usage_file(monkeypatch):
    yield
    (ROOT / "tests" / "_usage_unused.jsonl").unlink(missing_ok=True)


def test_recorder_stores_streamed_chunks_with_the_reply(tmp_path: Path) -> None:
    record = load_recorder()
    source = write_recording(tmp_path / "s.json", [(AIMessage(content="".join(TEXT_PIECES), id="run-b"), TEXT_CHUNKS)])
    recorder = record.Recorder("00-test", "ch00/x.py")
    model = ReplayModel.from_recording(source)
    list(model.stream("hi", config={"callbacks": [recorder]}))
    steps = recorder.model_steps()
    assert len(steps) == 1
    assert [json.loads(json.dumps(c))["data"]["content"] for c in steps[0]["chunks"]] == [c.content for c in TEXT_CHUNKS]
    assert json.loads(steps[0]["text"])["data"]["content"] == "".join(TEXT_PIECES)


def test_recorder_without_streaming_stores_no_chunks(tmp_path: Path) -> None:
    record = load_recorder()
    source = write_recording(tmp_path / "s.json", [(AIMessage(content="plain", id="p"), [])])
    recorder = record.Recorder("00-test", "ch00/x.py")
    ReplayModel.from_recording(source).invoke("hi", config={"callbacks": [recorder]})
    assert "chunks" not in recorder.model_steps()[0]


def test_two_models_with_one_recorder_keep_global_order(tmp_path: Path) -> None:
    record = load_recorder()
    source = write_recording(tmp_path / "s.json", [(AIMessage(content=text, id=text), []) for text in ("one", "two", "three")])
    recorder = record.Recorder("00-test", "ch00/x.py")
    first, second = ReplayModel.from_recording(source), ReplayModel.from_recording(source)
    for model in (first, second, first):
        model.invoke("q", config={"callbacks": [recorder]})
    assert [json.loads(s["text"])["data"]["content"] for s in recorder.model_steps()] == ["one", "two", "three"]
    # The saved recording replays in the same order for two fresh instances.
    out = tmp_path / "out.json"
    out.write_text(json.dumps({"steps": recorder.model_steps()}))
    ReplayModel.forget_tapes()
    a, b = ReplayModel.from_recording(out), ReplayModel.from_recording(out)
    assert [m.invoke("q").content for m in (a, b, a)] == ["one", "two", "three"]


def test_model_label_none_standin_and_real() -> None:
    record = load_recorder()
    real = AIMessage(content="x", response_metadata={"model_name": "deepseek-flash"})
    assert record.model_label([], model_used=False) == "none"
    assert record.model_label([], model_used=True) == "stand-in (no model)"
    assert record.model_label([AIMessage(content="x")], model_used=True) == "stand-in (no model)"
    assert record.model_label([real], model_used=True) == "deepseek-flash"
