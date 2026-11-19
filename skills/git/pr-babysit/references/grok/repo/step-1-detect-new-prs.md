# Step 1 — Detect New Pull Requests (repo lane)

Detect newly opened pull requests either in real time via GitHub CLI webhook forwarding or on demand via GitHub API polling.

## Method A — GitHub Webhook Forwarding (Real-Time)

Forward pull request events directly to the local receiver without opening public inbound ports.

### 1. Ensure `cli/gh-webhook` extension is installed

```bash
gh extension install cli/gh-webhook
```

### 2. Start the local receiver

Launch the local listener script in the background or as a systemd service:

```bash
python3 <dirname of SKILL.md>/scripts/webhook_receiver.py --port 8080
```

### 3. Forward repository pull_request events

```bash
gh webhook forward \
  --repo=<owner/repo> \
  --events=pull_request \
  --url=http://127.0.0.1:8080/
```

When a pull request opens or re-opens, the webhook payload delivers to the receiver, which executes the dispatch procedure in Step 2.

## Method B — CLI / REST Polling (Interval Fallback)

When running on repositories without webhook administrative access:

### Query open PRs

```bash
gh pr list --repo <owner/repo> --state open --json number,title,headRefName,url --limit 20
```

### Diff against known PRs

Compare the returned PR numbers with the `known_prs` array in `~/.agents/develop/repo-watchlist.json`.

For each number not in `known_prs`:
1. Record the number in `known_prs` immediately to avoid duplicate dispatch.
2. Trigger the session dispatch sequence in Step 2.

## Next

Continue to Step 2 (spawn session) in `repo/`.
