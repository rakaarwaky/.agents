#!/usr/bin/env python3
"""GitHub Webhook receiver for pr-babysit repo watchlist.

Listens for GitHub pull_request events forwarded via `gh webhook forward`
and dispatches isolated Grok sessions in Orca worktrees running `/pr-babysit add <number>`.
"""

import argparse
import hashlib
import hmac
import json
import logging
import os
import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("pr-babysit-webhook")

DEFAULT_PORT = 8080
DEFAULT_WORKSPACE = "/home/raka/.agents"
STATE_DIR = Path.home() / ".agents" / "develop"
WATCHLIST_FILE = STATE_DIR / "repo-watchlist.json"


def resolve_orca_cli() -> str:
    """Resolve the Orca CLI executable following workspace conventions."""
    orca_env = os.environ.get("ORCA_CLI_COMMAND")
    if orca_env and os.path.exists(orca_env) and os.access(orca_env, os.X_OK):
        return orca_env

    shim = Path.home() / ".config" / "orca" / "linux-orca-cli-shim" / "orca"
    if shim.exists() and os.access(shim, os.X_OK):
        return str(shim)

    orca_ide = shutil.which("orca-ide")
    if orca_ide:
        return orca_ide

    return "orca"


def load_watchlist() -> dict:
    """Load the watched repositories from state file."""
    if not WATCHLIST_FILE.exists():
        return {"watched_repos": {}}
    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Failed to parse watchlist file %s: %s", WATCHLIST_FILE, exc)
        return {"watched_repos": {}}


def save_watchlist(data: dict) -> None:
    """Persist watchlist updates to state file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp_path = WATCHLIST_FILE.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    tmp_path.replace(WATCHLIST_FILE)


def record_pr_seen(repo_name: str, pr_number: int) -> bool:
    """Check if PR is already known; record and return True if new."""
    watchlist = load_watchlist()
    repos = watchlist.setdefault("watched_repos", {})
    repo_entry = repos.setdefault(repo_name.lower(), {"known_prs": []})

    if pr_number in repo_entry["known_prs"]:
        return False

    repo_entry["known_prs"].append(pr_number)
    save_watchlist(watchlist)
    return True


class WebhookHandler(BaseHTTPRequestHandler):
    secret: str = ""
    workspace: str = DEFAULT_WORKSPACE
    dry_run: bool = False

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        if self.secret:
            signature = self.headers.get("X-Hub-Signature-256", "")
            computed = "sha256=" + hmac.new(self.secret.encode(), body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, computed):
                logger.warning("Signature validation failed for request")
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Invalid signature")
                return

        event = self.headers.get("X-GitHub-Event", "")
        if event != "pull_request":
            logger.info("Ignoring unhandled event type: %s", event)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Ignored")
            return

        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception as exc:
            logger.error("Failed to parse JSON payload: %s", exc)
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        action = payload.get("action")
        if action not in ("opened", "reopened"):
            logger.info("Ignoring pull_request action: %s", action)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Ignored action")
            return

        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        pr_number = pr.get("number")
        pr_url = pr.get("html_url")
        repo_full = repo.get("full_name")
        repo_slug = repo.get("name")

        if not pr_number or not repo_full:
            logger.error("Missing PR number or repository full_name in payload")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing PR fields")
            return

        logger.info("Received %s event: PR #%s on %s (%s)", action, pr_number, repo_full, pr_url)

        is_new = record_pr_seen(repo_full, pr_number)
        if not is_new:
            logger.info("PR #%s on %s was already processed; skipping dispatch", pr_number, repo_full)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Already processed")
            return

        self.spawn_babysit_session(repo_slug, pr_number, pr_url)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Dispatched")

    def spawn_babysit_session(self, repo_slug: str, pr_number: int, pr_url: str) -> None:
        worktree_name = f"pr-babysit-{repo_slug}-{pr_number}"
        prompt = f"/pr-babysit add {pr_number}"
        orca_cmd = resolve_orca_cli()

        cmd = [
            orca_cmd,
            "worktree",
            "create",
            "--repo",
            f"path:{self.workspace}",
            "--name",
            worktree_name,
            "--agent",
            "grok",
            "--prompt",
            prompt,
            "--no-parent",
            "--json",
        ]

        logger.info("Spawning session: %s", " ".join(cmd))
        if self.dry_run:
            logger.info("[Dry Run] Would execute: %s", cmd)
            return

        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Orca worktree creation succeeded: %s", proc.stdout.strip())
        except subprocess.CalledProcessError as exc:
            logger.error("Failed to spawn Orca worktree: %s", exc.stderr.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="PR Babysit GitHub Webhook Receiver")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", DEFAULT_PORT)), help="Port to listen on")
    parser.add_argument("--secret", type=str, default=os.environ.get("GITHUB_WEBHOOK_SECRET", ""), help="Webhook secret")
    parser.add_argument("--workspace", type=str, default=DEFAULT_WORKSPACE, help="Agents workspace path")
    parser.add_argument("--dry-run", action="store_true", help="Log commands instead of creating worktrees")
    args = parser.parse_args()

    WebhookHandler.secret = args.secret
    WebhookHandler.workspace = args.workspace
    WebhookHandler.dry_run = args.dry_run

    server_address = ("127.0.0.1", args.port)
    httpd = HTTPServer(server_address, WebhookHandler)
    logger.info("Webhook receiver listening on http://127.0.0.1:%d", args.port)
    logger.info("Using Orca CLI: %s", resolve_orca_cli())
    logger.info("Target workspace: %s", args.workspace)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down webhook receiver")
        httpd.server_close()


if __name__ == "__main__":
    main()
