"""Tests for envdiff.snapshot — save/load environment snapshots."""

import json
import pytest
from pathlib import Path

from envdiff.snapshot import (
    save_snapshot,
    load_snapshot,
    snapshot_metadata,
    SNAPSHOT_VERSION,
)


SAMPLE_ENV = {"APP_ENV": "production", "PORT": "8080", "DEBUG": "false"}


@pytest.fixture()
def snapshot_path(tmp_path: Path) -> Path:
    return tmp_path / "envdiff_snapshots" / "prod.json"


def test_save_creates_file(snapshot_path: Path) -> None:
    save_snapshot(SAMPLE_ENV, snapshot_path)
    assert snapshot_path.exists()


def test_save_creates_parent_dirs(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b" / "c" / "snap.json"
    save_snapshot(SAMPLE_ENV, deep)
    assert deep.exists()


def test_save_round_trip(snapshot_path: Path) -> None:
    save_snapshot(SAMPLE_ENV, snapshot_path)
    loaded = load_snapshot(snapshot_path)
    assert loaded == SAMPLE_ENV


def test_save_includes_version(snapshot_path: Path) -> None:
    save_snapshot(SAMPLE_ENV, snapshot_path)
    raw = json.loads(snapshot_path.read_text())
    assert raw["version"] == SNAPSHOT_VERSION


def test_save_includes_label(snapshot_path: Path) -> None:
    save_snapshot(SAMPLE_ENV, snapshot_path, label="my-prod-snapshot")
    raw = json.loads(snapshot_path.read_text())
    assert raw["label"] == "my-prod-snapshot"


def test_save_default_label_is_path(snapshot_path: Path) -> None:
    save_snapshot(SAMPLE_ENV, snapshot_path)
    raw = json.loads(snapshot_path.read_text())
    assert str(snapshot_path) in raw["label"]


def test_load_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_snapshot(tmp_path / "nonexistent.json")


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    with pytest.raises(Exception):
        load_snapshot(bad)


def test_load_missing_env_key_raises(tmp_path: Path) -> None:
    bad = tmp_path / "no_env.json"
    bad.write_text(json.dumps({"version": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="missing 'env' key"):
        load_snapshot(bad)


def test_metadata_returns_key_count(snapshot_path: Path) -> None:
    save_snapshot(SAMPLE_ENV, snapshot_path)
    meta = snapshot_metadata(snapshot_path)
    assert meta["key_count"] == len(SAMPLE_ENV)


def test_metadata_returns_created_at(snapshot_path: Path) -> None:
    save_snapshot(SAMPLE_ENV, snapshot_path)
    meta = snapshot_metadata(snapshot_path)
    assert meta["created_at"] is not None
    assert "T" in str(meta["created_at"])  # ISO-8601 check
