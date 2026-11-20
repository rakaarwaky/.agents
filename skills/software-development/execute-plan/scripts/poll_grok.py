#!/usr/bin/env python3
"""Poll an Orca terminal until Grok Build finishes the /execute-plan loop.

Usage:
    python3 poll_grok.py <terminal_handle> [--orca <path>] [--deadline-hours 2]

Exit 0 on success (completion detected or terminal exited cleanly), 2 on
error/timeout. Prints periodic progress to stderr so background notify
messages stay useful.

Completion is detected from EITHER a literal EXECUTE_PLAN_COMPLETE sentinel OR
a final-report shape (a GitHub PR URL / "Draft PR" reference rendered on screen
while the agent is idle). Many Grok runs end with a per-PR summary table and a
"Draft PR: #N" line and never emit the literal sentinel — relying on the
sentinel alone yields a false timeout on a run that actually succeeded.
A `terminal wait --for tui-idle` that returns not-satisfied means the agent is
BUSY, not that the poll failed; only a genuine CLI/parse failure counts as an
error.
"""
import argparse
import json
import subprocess
import sys
import time


def orca_run(args: list[str]) -> dict:
    """Return parsed JSON, or {} on CLI/parse failure (a real error)."""
    try:
        out = subprocess.run(args, capture_output=True, text=True, timeout=90)
        return json.loads(out.stdout) if out.stdout.strip() else {}
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        return {}


def screen_text(read_res: dict) -> str:
    terminal = read_res.get("result", {}).get("terminal", {})
    return "\n".join(terminal.get("tail", []))


def has_final_report(text: str) -> bool:
    """Heuristic for Grok's end-of-run report block on the rendered screen."""
    lowered = text.lower()
    pr_markers = (
        "draft pr",
        "draft: #",
        "pr #",
        "pull request",
        "github.com/",
    )
    has_pr = any(m in lowered for m in pr_markers)
    # A finished run shows a settled prompt line and a worked-duration marker.
    settled = "worked for" in lowered or "─ myomniroute" in text or "always-approve" in lowered
    return has_pr and settled


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("handle")
    parser.add_argument("--orca", default=None)
    parser.add_argument("--deadline-hours", type=int, default=2)
    parser.add_argument("--wait-ms", type=int, default=15000,
                        help="tui-idle wait timeout per cycle (busy != error)")
    parser.add_argument("--idle-confirm", type=int, default=2,
                        help="consecutive idle+report cycles before declaring done")
    args = parser.parse_args()

    orca = args.orca
    if not orca:
        import os
        orca = os.environ.get(
            "ORCA_CLI_COMMAND",
            os.environ.get("ORCA", "orca-ide"),
        )

    deadline = time.monotonic() + args.deadline_hours * 3600
    cli_errors = 0            # only genuine CLI/parse failures increment this
    report_idle_cycles = 0    # idle cycles that ALSO show a final report

    while time.monotonic() < deadline:
        # A full-screen TUI agent renders to its terminal SCREEN, not the line
        # stream. `--cursor` returns only the PTY line stream (for a TUI agent
        # that is just the shell launch echo, cursor stuck at 1), so use
        # `--screen` — the only mode that surfaces the agent's rendered output.
        read_res = orca_run([
            orca, "terminal", "read",
            "--terminal", args.handle,
            "--screen",
            "--json",
        ])
        if not read_res:
            cli_errors += 1
            if cli_errors >= 10:
                print("ERROR: 10 consecutive CLI failures reading terminal", file=sys.stderr)
                return 2
            time.sleep(10)
            continue
        cli_errors = 0

        text = screen_text(read_res)
        if "EXECUTE_PLAN_COMPLETE" in text:
            print("SENTINEL: EXECUTE_PLAN_COMPLETE", file=sys.stderr)
            for line in text.splitlines()[-50:]:
                print(line, file=sys.stderr)
            return 0

        terminal = read_res.get("result", {}).get("terminal", {})
        if terminal.get("status") == "exited":
            # Terminal gone: success only if a final report was on screen.
            if has_final_report(text):
                print("DONE: terminal exited with final report on screen", file=sys.stderr)
                for line in text.splitlines()[-50:]:
                    print(line, file=sys.stderr)
                return 0
            print("ERROR: terminal exited without a final report — run failed", file=sys.stderr)
            for line in text.splitlines()[-20:]:
                print(line, file=sys.stderr)
            return 2

        # Pace the loop. A not-satisfied result = agent still busy, NOT an error.
        wait_res = orca_run([
            orca, "terminal", "wait",
            "--terminal", args.handle,
            "--for", "tui-idle",
            "--timeout-ms", str(args.wait_ms),
            "--json",
        ])
        satisfied = bool(wait_res.get("result", {}).get("wait", {}).get("satisfied"))

        if satisfied and has_final_report(text):
            report_idle_cycles += 1
            elapsed = time.monotonic() - (deadline - args.deadline_hours * 3600)
            print(f"[{elapsed:.0f}s] idle+report cycle {report_idle_cycles}/{args.idle_confirm}",
                  file=sys.stderr)
            if report_idle_cycles >= args.idle_confirm:
                print("DONE: final report detected on idle screen", file=sys.stderr)
                for line in text.splitlines()[-50:]:
                    print(line, file=sys.stderr)
                return 0
        else:
            # Either busy, or idle mid-turn without a report yet — keep polling.
            report_idle_cycles = 0
            elapsed = time.monotonic() - (deadline - args.deadline_hours * 3600)
            state = "idle" if satisfied else "busy"
            print(f"[{elapsed:.0f}s] Grok {state} (no final report yet)", file=sys.stderr)

        time.sleep(10)

    print("ERROR: polling deadline exceeded", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
