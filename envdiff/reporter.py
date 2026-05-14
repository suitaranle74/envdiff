"""Formats and renders EnvDiffResult into human-readable or machine-readable output."""

from __future__ import annotations

import json
from typing import Literal

from envdiff.diff import EnvDiffResult

OutputFormat = Literal["text", "json", "compact"]


def _status_icon(status: str) -> str:
    icons = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    return icons.get(status, "?")


def render_text(result: EnvDiffResult, show_unchanged: bool = False) -> str:
    """Render a human-readable diff report."""
    lines: list[str] = []
    lines.append(f"Comparing: {result.left_label!r} vs {result.right_label!r}")
    lines.append("-" * 60)

    for key in sorted(result.all_keys):
        entry = result.entries[key]
        status = entry["status"]
        if status == "unchanged" and not show_unchanged:
            continue
        icon = _status_icon(status)
        if status == "changed":
            lines.append(f"  {icon} {key}")
            lines.append(f"      left : {entry['left']!r}")
            lines.append(f"      right: {entry['right']!r}")
        elif status == "added":
            lines.append(f"  {icon} {key}={entry['right']!r}")
        elif status == "removed":
            lines.append(f"  {icon} {key}={entry['left']!r}")
        else:
            lines.append(f"  {icon} {key}={entry['left']!r}")

    lines.append("-" * 60)
    lines.append(
        f"Summary: {result.added} added, {result.removed} removed, "
        f"{result.changed} changed, {result.unchanged} unchanged"
    )
    return "\n".join(lines)


def render_json(result: EnvDiffResult) -> str:
    """Render a JSON-serialisable diff report."""
    payload = {
        "left_label": result.left_label,
        "right_label": result.right_label,
        "summary": {
            "added": result.added,
            "removed": result.removed,
            "changed": result.changed,
            "unchanged": result.unchanged,
            "has_drift": result.has_drift,
        },
        "entries": result.entries,
    }
    return json.dumps(payload, indent=2)


def render_compact(result: EnvDiffResult) -> str:
    """One-line-per-key compact format (status KEY)."""
    lines: list[str] = []
    for key in sorted(result.all_keys):
        status = result.entries[key]["status"]
        if status != "unchanged":
            lines.append(f"{status.upper():10s} {key}")
    return "\n".join(lines) if lines else "(no drift detected)"


def render(result: EnvDiffResult, fmt: OutputFormat = "text", **kwargs) -> str:
    """Dispatch to the requested renderer."""
    if fmt == "json":
        return render_json(result)
    if fmt == "compact":
        return render_compact(result)
    return render_text(result, **kwargs)
