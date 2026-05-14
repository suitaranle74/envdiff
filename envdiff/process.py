"""Read environment variables from a running process."""

import os
from pathlib import Path
from typing import Dict


def read_process_env(pid: int) -> Dict[str, str]:
    """Read environment variables of a running process via /proc/<pid>/environ.

    Args:
        pid: Process ID to inspect.

    Returns:
        Dictionary of environment variable names to values.

    Raises:
        FileNotFoundError: If the process does not exist or is inaccessible.
        PermissionError: If the current user cannot read the process environ.
    """
    environ_path = Path(f"/proc/{pid}/environ")
    if not environ_path.exists():
        raise FileNotFoundError(
            f"No such process or /proc entry not found for PID {pid}"
        )

    raw = environ_path.read_bytes()
    result: Dict[str, str] = {}
    for entry in raw.split(b"\x00"):
        if not entry:
            continue
        try:
            decoded = entry.decode("utf-8")
        except UnicodeDecodeError:
            decoded = entry.decode("latin-1")
        if "=" in decoded:
            key, _, value = decoded.partition("=")
            result[key] = value
    return result


def current_process_env() -> Dict[str, str]:
    """Return the environment of the current process."""
    return dict(os.environ)
