"""Tests for envdiff.reporter and envdiff.cli."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from envdiff.diff import diff_envs
from envdiff.reporter import render, render_compact, render_json, render_text


@pytest.fixture()
def sample_result():
    left = {"A": "1", "B": "old", "C": "same"}
    right = {"B": "new", "C": "same", "D": "added"}
    return diff_envs(left, right, left_label=".env.left", right_label=".env.right")


# --- reporter tests ---

def test_render_text_contains_labels(sample_result):
    out = render_text(sample_result)
    assert ".env.left" in out
    assert ".env.right" in out


def test_render_text_shows_drift_keys(sample_result):
    out = render_text(sample_result)
    assert "A" in out   # removed
    assert "B" in out   # changed
    assert "D" in out   # added


def test_render_text_hides_unchanged_by_default(sample_result):
    out = render_text(sample_result, show_unchanged=False)
    assert "C" not in out


def test_render_text_shows_unchanged_when_requested(sample_result):
    out = render_text(sample_result, show_unchanged=True)
    assert "C" in out


def test_render_json_is_valid_json(sample_result):
    raw = render_json(sample_result)
    data = json.loads(raw)
    assert data["left_label"] == ".env.left"
    assert data["summary"]["has_drift"] is True
    assert "entries" in data


def test_render_compact_no_drift():
    result = diff_envs({"X": "1"}, {"X": "1"})
    assert render_compact(result) == "(no drift detected)"


def test_render_compact_shows_status_labels(sample_result):
    out = render_compact(sample_result)
    assert "ADDED" in out or "REMOVED" in out or "CHANGED" in out


def test_render_dispatch_text(sample_result):
    out = render(sample_result, fmt="text")
    assert "Summary" in out


def test_render_dispatch_json(sample_result):
    out = render(sample_result, fmt="json")
    json.loads(out)  # must not raise


def test_render_dispatch_compact(sample_result):
    out = render(sample_result, fmt="compact")
    assert isinstance(out, str)


# --- CLI tests ---

def test_cli_files_no_drift(tmp_path):
    from envdiff.cli import main

    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("KEY=value\n")
    f2.write_text("KEY=value\n")
    with pytest.raises(SystemExit) as exc:
        main(["files", str(f1), str(f2)])
    assert exc.value.code == 0


def test_cli_files_with_drift(tmp_path):
    from envdiff.cli import main

    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("KEY=old\n")
    f2.write_text("KEY=new\n")
    with pytest.raises(SystemExit) as exc:
        main(["files", str(f1), str(f2)])
    assert exc.value.code == 1


def test_cli_proc_current(tmp_path):
    from envdiff.cli import main

    f1 = tmp_path / "a.env"
    f1.write_text("ENVDIFF_TEST_VAR=hello\n")
    with patch("envdiff.cli.current_process_env", return_value={"ENVDIFF_TEST_VAR": "hello"}):
        with pytest.raises(SystemExit) as exc:
            main(["proc", str(f1)])
    assert exc.value.code == 0
