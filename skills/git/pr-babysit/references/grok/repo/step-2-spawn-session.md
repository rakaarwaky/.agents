# Step 2 — Spawn Grok Session for New Pull Request (repo lane)

Upon detecting a new pull request on a watched repository, spawn an isolated Grok agent session running the `add` mode of `pr-babysit`.

## Step 2.1 — Resolve execution parameters

Extract repository identifier and PR number:
- `REPO_SLUG`: base name of the repository (e.g. `foo` from `owner/foo`)
- `PR_NUMBER`: integer pull request number (e.g. `42`)
- `AGENT_WORKSPACE`: default `/home/raka/.agents`

Set the worktree identifier:
```text
WORKTREE_NAME="pr-babysit-<REPO_SLUG>-<PR_NUMBER>"
PROMPT="/pr-babysit add <PR_NUMBER>"
```

## Step 2.2 — Spawn isolated session in Orca worktree

Execute `orca worktree create`:

```bash
$ORCA_CLI_COMMAND worktree create \
  --repo path:/home/raka/.agents \
  --name "$WORKTREE_NAME" \
  --agent grok \
  --prompt "$PROMPT" \
  --no-parent \
  --json
```

Where `$ORCA_CLI_COMMAND` resolves to the workspace Orca CLI shim (`/home/raka/.config/orca/linux-orca-cli-shim/orca`).

The command:
1. Provisions an isolated git worktree for the pull request.
2. Initializes the Grok agent inside the worktree.
3. Automatically delivers the prompt `/pr-babysit add <PR_NUMBER>` to the TUI.

## Step 2.3 — Alternative headless dispatch

When executing without an Orca desktop instance:

```bash
grok -p "/pr-babysit add <PR_NUMBER>" --cwd /home/raka/.agents
```

## Step 2.4 — Log and update state

Record dispatch outcome in `~/.agents/develop/repo-watchlist.json`:
- Timestamp of dispatch
- Generated worktree name or process ID
- Pull request URL

The spawned agent session assumes responsibility for watching CI, addressing review comments, and applying auto-fixes per `references/grok/add/`.
