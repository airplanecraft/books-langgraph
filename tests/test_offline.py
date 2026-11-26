"""Runs every recorded example offline and checks it prints exactly what the book shows.
Book: Chapter 0, section 0.1
Run: python -m pytest
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
RECORDINGS = sorted(path for path in (ROOT / "replay").glob("ch*/*.json"))


@pytest.mark.parametrize("recording", RECORDINGS, ids=lambda path: f"{path.parent.name}/{path.stem}")
def test_offline_output_matches_the_book(recording: Path) -> None:
    script = ROOT / recording.parent.name / f"{recording.stem}.py"
    steps = json.loads(recording.read_text())["steps"]
    expected = [step["text"] for step in steps if step["kind"] == "stdout"]
    result = subprocess.run([sys.executable, str(script)], cwd=ROOT, env={**os.environ, "OFFLINE": "1"},
                            capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == expected


def test_every_recording_matches_its_script() -> None:
    for recording in RECORDINGS:
        script = ROOT / recording.parent.name / f"{recording.stem}.py"
        code = next(step["text"] for step in json.loads(recording.read_text())["steps"] if step["kind"] == "code")
        assert code == script.read_text(), f"{script.name} changed after it was recorded; record it again"
