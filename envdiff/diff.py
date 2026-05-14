"""Core diff logic for comparing two environment variable dictionaries."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class EnvDiffResult:
    """Result of comparing two environment variable sets."""

    only_in_left: Dict[str, str] = field(default_factory=dict)
    only_in_right: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, Tuple[str, str]] = field(default_factory=dict)  # key -> (left, right)
    matching: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        """Return True if any differences were found."""
        return bool(self.only_in_left or self.only_in_right or self.changed)

    def summary(self) -> str:
        lines = []
        lines.append(
            f"Drift detected: {self.has_drift} | "
            f"only_left={len(self.only_in_left)} "
            f"only_right={len(self.only_in_right)} "
            f"changed={len(self.changed)} "
            f"matching={len(self.matching)}"
        )
        return lines[0]


def diff_envs(
    left: Dict[str, str],
    right: Dict[str, str],
) -> EnvDiffResult:
    """Compare two environment variable dictionaries.

    Args:
        left: First set of environment variables (e.g. from a .env file).
        right: Second set (e.g. from a running process).

    Returns:
        An EnvDiffResult describing the differences.
    """
    result = EnvDiffResult()
    all_keys = set(left) | set(right)

    for key in sorted(all_keys):
        in_left = key in left
        in_right = key in right

        if in_left and not in_right:
            result.only_in_left[key] = left[key]
        elif in_right and not in_left:
            result.only_in_right[key] = right[key]
        elif left[key] != right[key]:
            result.changed[key] = (left[key], right[key])
        else:
            result.matching.append(key)

    return result
