"""Tests for chapter 8: the claims of the text about copies, sources and step numbers.
Book: Chapter 8, section 8.3
Run: python -m pytest tests/test_ch08_claims.py
"""
import contextlib
import io
import runpy
from pathlib import Path

from common import say

ROOT = Path(__file__).parent.parent


def run_ticket() -> dict:
    """Run ch08/history.py in this process, with a second scripted reply."""
    with contextlib.redirect_stdout(io.StringIO()):
        names = runpy.run_path(str(ROOT / "ch08" / "history.py"))
    names["model"].script.append(say("A second reply."))
    return names


def test_history_claims_of_the_text() -> None:
    names = run_ticket()
    graph, config = names["graph"], names["config"]
    history = list(graph.get_state_history(config))
    assert [s.metadata["step"] for s in history] == [3, 2, 1, 0, -1]
    assert [s.metadata["source"] for s in history] == ["loop"] * 4 + ["input"]
    assert history[0].next == () and names["before_draft"].next == ("draft",)
    before = names["before_draft"]
    graph.invoke(None, before.config)
    after = list(graph.get_state_history(config))
    assert [(s.metadata["step"], s.metadata["source"]) for s in after[:3]] == [
        (4, "loop"), (3, "loop"), (2, "fork")]
    assert len(after) == 8 and graph.get_state(config).config == after[0].config
    assert sum(1 for s in after if s.next == ("draft",)) == 2


def test_update_state_goes_through_the_reducer_and_keeps_old_copies() -> None:
    names = run_ticket()
    graph, config, before = names["graph"], names["config"], names["before_draft"]
    copy = graph.update_state(before.config, {"notes": ["by hand"]})
    snapshot = graph.get_state(copy)
    assert snapshot.metadata["source"] == "update" and snapshot.metadata["step"] == 2
    assert snapshot.values["notes"] == ["classified", "by hand"]
    assert len(list(graph.get_state_history(config))) == 6


def test_fork_copy_is_a_copy_of_the_chosen_one() -> None:
    names = run_ticket()
    graph, config, before = names["graph"], names["config"], names["before_draft"]
    graph.invoke(None, before.config)
    after = list(graph.get_state_history(config))
    waiting = [s for s in after if s.next == ("draft",)]
    assert len(waiting) == 2 and waiting[0].values == waiting[1].values
    assert [s.metadata["source"] for s in waiting] == ["fork", "loop"]
    assert waiting[0].parent_config == before.config


def test_run_from_newest_copy_saves_a_fork_copy() -> None:
    names = run_ticket()
    graph, config = names["graph"], names["config"]
    newest = list(graph.get_state_history(config))[0]
    graph.invoke(None, newest.config)
    sources = [s.metadata["source"] for s in graph.get_state_history(config)]
    assert len(sources) == 6 and sources[0] == "fork"
