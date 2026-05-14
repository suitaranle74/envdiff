"""Parser for .env files into key-value dictionaries."""

import re
from pathlib import Path
from typing import Dict, Optional


_LINE_RE = re.compile(
    r"^\s*(?:export\s+)?"
    r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*=\s*"
    r"(?P<value>.*)\s*$"
)
_COMMENT_RE = re.compile(r"^\s*#")


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """Parse a .env file and return a dict of key-value pairs.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary mapping variable names to their string values.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains a malformed line.
    """
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"env file not found: {path}")

    result: Dict[str, str] = {}
    with env_path.open(encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")
            # Skip blank lines and comments
            if not line.strip() or _COMMENT_RE.match(line):
                continue
            m = _LINE_RE.match(line)
            if not m:
                raise ValueError(
                    f"malformed line {lineno} in {path!r}: {line!r}"
                )
            key = m.group("key")
            value = _strip_quotes(m.group("value").strip())
            result[key] = value

    return result


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse env variable definitions from a raw string.

    Useful for testing or piped input.
    """
    result: Dict[str, str] = {}
    for lineno, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or _COMMENT_RE.match(line):
            continue
        m = _LINE_RE.match(line)
        if not m:
            raise ValueError(f"malformed line {lineno}: {line!r}")
        result[m.group("key")] = _strip_quotes(m.group("value").strip())
    return result
