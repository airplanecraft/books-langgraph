"""Removes the workspace/ folders that chapter scripts leave for the reader to look at, once the tests are done.
Book: Chapter 9, section 9.1
Run: python -m pytest   (pytest loads this file by itself)
"""
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session", autouse=True)
def remove_workspaces() -> Iterator[None]:
    """After the last test, delete every chNN/workspace/ folder."""
    yield
    for workspace in ROOT.glob("ch*/workspace"):
        shutil.rmtree(workspace, ignore_errors=True)
