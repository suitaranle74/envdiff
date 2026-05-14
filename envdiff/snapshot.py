"""Snapshot support: save and load environment variable sets to/from JSON files."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


SNAPSHOT_VERSION = 1


def save_snapshot(
    env: Dict[str, str],
    path: str | os.PathLike,
    label: Optional[str] = None,
) -> None:
    """Persist *env* as a JSON snapshot file at *path*.

    The file includes a metadata header so snapshots can be identified and
    compared later without ambiguity.
    """
    payload = {
        "version": SNAPSHOT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "label": label or str(path),
        "env": env,
    }
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_snapshot(path: str | os.PathLike) -> Dict[str, str]:
    """Load an environment dict from a previously saved snapshot file.

    Raises
    ------
    ValueError
        If the file does not look like a valid envdiff snapshot.
    FileNotFoundError
        If *path* does not exist.
    """
    src = Path(path)
    raw = json.loads(src.read_text(encoding="utf-8"))

    if not isinstance(raw, dict) or "env" not in raw:
        raise ValueError(
            f"{path!r} does not appear to be a valid envdiff snapshot "
            "(missing 'env' key)."
        )

    env = raw["env"]
    if not isinstance(env, dict):
        raise ValueError(f"'env' field in {path!r} must be a JSON object.")

    return {str(k): str(v) for k, v in env.items()}


def snapshot_metadata(path: str | os.PathLike) -> Dict[str, object]:
    """Return the metadata header of a snapshot without loading the full env."""
    src = Path(path)
    raw = json.loads(src.read_text(encoding="utf-8"))
    return {
        "version": raw.get("version"),
        "created_at": raw.get("created_at"),
        "label": raw.get("label"),
        "key_count": len(raw.get("env", {})),
    }
