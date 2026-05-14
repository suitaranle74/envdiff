"""Tests for envdiff.parser and envdiff.diff modules."""

import textwrap
import pytest

from envdiff.parser import parse_env_string, parse_env_file
from envdiff.diff import diff_envs, EnvDiffResult


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

class TestParseEnvString:
    def test_simple_pairs(self):
        src = "FOO=bar\nBAZ=qux\n"
        result = parse_env_string(src)
        assert result == {"FOO": "bar", "BAZ": "qux"}

    def test_export_prefix(self):
        result = parse_env_string("export MY_VAR=hello")
        assert result["MY_VAR"] == "hello"

    def test_double_quoted_value(self):
        result = parse_env_string('DB_URL="postgresql://localhost/mydb"')
        assert result["DB_URL"] == "postgresql://localhost/mydb"

    def test_single_quoted_value(self):
        result = parse_env_string("SECRET='top secret'")
        assert result["SECRET"] == "top secret"

    def test_comments_and_blanks_ignored(self):
        src = textwrap.dedent("""
            # this is a comment
            FOO=1

            # another comment
            BAR=2
        """)
        result = parse_env_string(src)
        assert result == {"FOO": "1", "BAR": "2"}

    def test_malformed_line_raises(self):
        with pytest.raises(ValueError, match="malformed line"):
            parse_env_string("THIS IS NOT VALID")

    def test_empty_value(self):
        result = parse_env_string("EMPTY=")
        assert result["EMPTY"] == ""


class TestParseEnvFile:
    def test_reads_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("KEY=value\nOTHER=123\n")
        result = parse_env_file(env_file)
        assert result == {"KEY": "value", "OTHER": "123"}

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            parse_env_file(tmp_path / "nonexistent.env")


# ---------------------------------------------------------------------------
# Diff tests
# ---------------------------------------------------------------------------

class TestDiffEnvs:
    def test_no_differences(self):
        env = {"A": "1", "B": "2"}
        result = diff_envs(env, env.copy())
        assert not result.has_drift
        assert sorted(result.matching) == ["A", "B"]

    def test_only_in_left(self):
        result = diff_envs({"A": "1"}, {})
        assert result.only_in_left == {"A": "1"}
        assert result.has_drift

    def test_only_in_right(self):
        result = diff_envs({}, {"B": "2"})
        assert result.only_in_right == {"B": "2"}
        assert result.has_drift

    def test_changed_value(self):
        result = diff_envs({"X": "old"}, {"X": "new"})
        assert result.changed == {"X": ("old", "new")}
        assert result.has_drift

    def test_mixed_differences(self):
        left = {"SHARED": "same", "LEFT_ONLY": "x", "CHANGED": "v1"}
        right = {"SHARED": "same", "RIGHT_ONLY": "y", "CHANGED": "v2"}
        result = diff_envs(left, right)
        assert result.matching == ["SHARED"]
        assert result.only_in_left == {"LEFT_ONLY": "x"}
        assert result.only_in_right == {"RIGHT_ONLY": "y"}
        assert result.changed == {"CHANGED": ("v1", "v2")}

    def test_summary_contains_drift_flag(self):
        result = diff_envs({"A": "1"}, {"A": "2"})
        summary = result.summary()
        assert "Drift detected: True" in summary
