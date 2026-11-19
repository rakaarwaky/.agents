#!/usr/bin/env python3
"""Poll an Orca terminal until Grok Build finishes the /execute-plan loop.

Usage:
    python3 poll_grok.py <terminal_handle> [--orca <path>] [--deadline-hours 2]

Exit 0 on success (sentinel seen or terminal exited), 2 on error/timeout.
Prints periodic progress to stderr so background notify messages stay useful.
"""
import argparse
import json
import subprocess
import sys
import time


def orca_run(args: list[str]) -> dict:
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=90)
        return json.loads(out.stdout) if out.stdout.strip() else {}
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        return {}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("handle")
    parser.add_argument("--orca", default=None)
    parser.add_argument("--deadline-hours", type=int, default=2)
    args = parser.parse_args()

    orca = args.orca
    if not orca:
        import os
        orca = os.environ.get(
            "ORCA_CLI_COMMAND",
            os.environ.get("ORCA", "orca-ide"),
        )

    deadline = time.monotonic() + args.deadline_hours * 3600
    consecutive_errors = 0
    idle_cycles = 0

    while time.monotonic() < deadline:
        # A full-screen TUI agent renders to its terminal SCREEN, not the line
        # stream. `terminal read --cursor` returns only the PTY line stream (for a
        # TUI agent that is just the shell launch echo, cursor stuck at 1), so the
        # sentinel is invisible there. Use `--screen` — the only mode that surfaces
        # the agent's rendered output and the EXECUTE_PLAN_COMPLETE sentinel.
        read_res = orca_run([
            orca, "terminal", "read",
            "--terminal", args.handle,
            "--screen",
            "--json",
        ])
        terminal = read_res.get("result", {}).get("terminal", {})

        # Sentinel check against the rendered screen
        if "EXECUTE_PLAN_COMPLETE" in json.dumps(read_res):
            print("SENTINEL: EXECUTE_PLAN_COMPLETE", file=sys.stderr)
            # Drain final output
            for line in terminal.get("tail", [])[-50:]:
                print(line, file=sys.stderr)
            return 0

        status = terminal.get("status", "unknown")

        if status == "exited":
            print("ERROR: terminal exited without sentinel — run failed", file=sys.stderr)
            for line in terminal.get("tail", [])[-20:]:
                print(line, file=sys.stderr)
            return 2

        # Check idle
        wait_res = orca_run([
            orca, "terminal", "wait",
            "--terminal", args.handle,
            "--for", "tui-idle",
            "--timeout-ms", "60000",
            "--json",
        ])
        satisfied = wait_res.get("result", {}).get("satisfied", False)

        if satisfied:
            idle_cycles += 1
            elapsed = time.monotonic() - (deadline - args.deadline_hours * 3600)
            print(f"[{elapsed:.0f}s] Grok idle (cycle {idle_cycles})", file=sys.stderr)
            consecutive_errors = 0
        else:
            idle_cycles = 0
            consecutive_errors += 1
            if consecutive_errors >= 30:
                print("ERROR: 30 consecutive wait failures — aborting", file=sys.stderr)
                return 2

        time.sleep(10)

    print("ERROR: polling deadline exceeded", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
