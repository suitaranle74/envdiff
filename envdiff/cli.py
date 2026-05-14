"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys

from envdiff.diff import diff_envs
from envdiff.parser import parse_env_file
from envdiff.process import current_process_env, read_process_env
from envdiff.reporter import render
from envdiff.snapshot import load_snapshot, save_snapshot


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare environment variable sets across .env files and processes.",
    )
    p.add_argument("--format", choices=["text", "json", "compact"], default="text")
    p.add_argument("--show-unchanged", action="store_true")

    sub = p.add_subparsers(dest="command", required=True)

    # files sub-command
    files_p = sub.add_parser("files", help="Diff two .env files.")
    files_p.add_argument("file_a", metavar="FILE_A")
    files_p.add_argument("file_b", metavar="FILE_B")

    # proc sub-command
    proc_p = sub.add_parser("proc", help="Diff a .env file against a running process.")
    proc_p.add_argument("env_file", metavar="ENV_FILE")
    proc_p.add_argument("pid", metavar="PID", type=int, nargs="?", default=None)

    # snapshot sub-commands
    snap_p = sub.add_parser("snapshot", help="Save or compare environment snapshots.")
    snap_sub = snap_p.add_subparsers(dest="snap_command", required=True)

    save_p = snap_sub.add_parser("save", help="Save current env to a snapshot file.")
    save_p.add_argument("output", metavar="OUTPUT_FILE")
    save_p.add_argument("--label", default=None)

    diff_p = snap_sub.add_parser("diff", help="Diff two snapshot files.")
    diff_p.add_argument("snapshot_a", metavar="SNAPSHOT_A")
    diff_p.add_argument("snapshot_b", metavar="SNAPSHOT_B")

    return p


def cmd_files(args: argparse.Namespace) -> int:
    env_a = parse_env_file(args.file_a)
    env_b = parse_env_file(args.file_b)
    result = diff_envs(env_a, env_b, label_a=args.file_a, label_b=args.file_b)
    print(render(result, fmt=args.format, show_unchanged=args.show_unchanged))
    return 0 if not result.has_drift else 1


def cmd_proc(args: argparse.Namespace) -> int:
    env_a = parse_env_file(args.env_file)
    env_b = read_process_env(args.pid) if args.pid else current_process_env()
    label_b = f"pid:{args.pid}" if args.pid else "current process"
    result = diff_envs(env_a, env_b, label_a=args.env_file, label_b=label_b)
    print(render(result, fmt=args.format, show_unchanged=args.show_unchanged))
    return 0 if not result.has_drift else 1


def cmd_snapshot(args: argparse.Namespace) -> int:
    if args.snap_command == "save":
        env = current_process_env()
        save_snapshot(env, args.output, label=args.label)
        print(f"Snapshot saved to {args.output!r} ({len(env)} keys).")
        return 0

    if args.snap_command == "diff":
        env_a = load_snapshot(args.snapshot_a)
        env_b = load_snapshot(args.snapshot_b)
        result = diff_envs(
            env_a, env_b, label_a=args.snapshot_a, label_b=args.snapshot_b
        )
        print(render(result, fmt=args.format, show_unchanged=args.show_unchanged))
        return 0 if not result.has_drift else 1

    return 1  # unknown snap_command


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {"files": cmd_files, "proc": cmd_proc, "snapshot": cmd_snapshot}
    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    sys.exit(handler(args))


if __name__ == "__main__":
    main()
