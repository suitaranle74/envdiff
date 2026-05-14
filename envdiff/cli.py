"""Command-line interface for envdiff."""

from __future__ import annotations

import argparse
import sys

from envdiff.diff import diff_envs
from envdiff.parser import parse_env_file
from envdiff.process import current_process_env, read_process_env
from envdiff.reporter import OutputFormat, render


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare environment variable sets across .env files and processes.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # files sub-command
    fc = sub.add_parser("files", help="Diff two .env files.")
    fc.add_argument("left", help="First .env file path.")
    fc.add_argument("right", help="Second .env file path.")
    fc.add_argument("-f", "--format", choices=["text", "json", "compact"], default="text")
    fc.add_argument("--show-unchanged", action="store_true")

    # proc sub-command
    pc = sub.add_parser("proc", help="Diff a .env file against a running process.")
    pc.add_argument("envfile", help=".env file path.")
    pc.add_argument("pid", type=int, nargs="?", default=None, help="PID (omit for current process).")
    pc.add_argument("-f", "--format", choices=["text", "json", "compact"], default="text")
    pc.add_argument("--show-unchanged", action="store_true")

    return p


def cmd_files(args: argparse.Namespace) -> int:
    left_env = parse_env_file(args.left)
    right_env = parse_env_file(args.right)
    result = diff_envs(left_env, right_env, left_label=args.left, right_label=args.right)
    fmt: OutputFormat = args.format
    print(render(result, fmt=fmt, show_unchanged=args.show_unchanged))
    return 1 if result.has_drift else 0


def cmd_proc(args: argparse.Namespace) -> int:
    left_env = parse_env_file(args.envfile)
    if args.pid is None:
        right_env = current_process_env()
        right_label = "current process"
    else:
        right_env = read_process_env(args.pid)
        right_label = f"pid:{args.pid}"
    result = diff_envs(left_env, right_env, left_label=args.envfile, right_label=right_label)
    fmt: OutputFormat = args.format
    print(render(result, fmt=fmt, show_unchanged=args.show_unchanged))
    return 1 if result.has_drift else 0


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "files":
        sys.exit(cmd_files(args))
    elif args.command == "proc":
        sys.exit(cmd_proc(args))
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
