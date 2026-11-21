# Delegate — hand tasks to workers and automate recurring work

Covers two jobs: handing code work to a worker in an Orca worktree, and building automations for anything that repeats or happens later. This file is read when the request is implementation work, a recurring task, or a wait on an event.

**Goal:** every request is either delegated to the right worker with a bounded brief, or turned into one named automation that runs in the right chat.

## Part A — delegate code work

### 1. Resolve the project and check for existing work

```bash
orca repo list
orca worktree ps --since 7d
```

If a worker is already on the task, message it instead of starting a second one:

```bash
orca orchestration send --to dispatch:<id> --type question --subject "..." --body "..."
```

### 2. Start a worker in a new worktree

Never edit project files in this bot's home (Rule R6). Start a worker on your own agent in a fresh workspace:

```bash
orca orchestration worker-start \
  --worktree new-child \
  --repo <project> \
  --agent grok \
  --spec "you own the pull request you open until it is ready to merge: watch its checks and reviews, fix what fails or is asked, then report"
```

Add `--on <server>` for a worker on another computer. After starting workers, end the turn — their results arrive as item mail, not in this chat.

### 3. Track on an item

```bash
orca bot item add --title "<deliverable>" --done-means "<checkable criterion>"
orca bot item link <n> dispatch:<id> <PR URL>
```

Put worker results on the item (`bot item comment <n> --text "..."`), never in chat.

## Part B — automate recurring or future work

### 1. Check the trigger options first

```bash
orca automations trigger-options --bot <your name>
```

Confirm in plain words what will start the run before creating anything. If no trigger fits, say so and offer the closest event or schedule.

### 2. Create one automation per request (Rule R2)

A wait on one event (`--once`, narrowest event):

```bash
orca automations create --bot <you> --name "<what it waits for>" --once \
  --on "github.ci_passed subject=<owner/repo#n>" \
  --prompt "..."
```

A recurring run (on a schedule):

```bash
orca automations create --bot <you> --name "..." \
  --on "schedule every 6h" \
  --prompt "..."
```

State where it runs (new conversation, this chat, or your Chat) and where results go. A run made answering a thread posts its final message to that thread.

### 3. Watch a pull request (owner asked you to)

One wait with all the transitions:

```bash
orca automations create --bot <you> --name "PR <owner/repo#n>" --once \
  --on "github.ci_passed subject=<owner/repo#n>" \
  --on "github.ci_failed subject=<owner/repo#n>" \
  --on "github.pr_conflicted subject=<owner/repo#n>" \
  --on "github.pr_merged subject=<owner/repo#n>" \
  --on "github.pr_closed subject=<owner/repo#n>" \
  --on "github.review subject=<owner/repo#n>" \
  --on "github.comment subject=<owner/repo#n>" \
  --prompt "read the PR with gh: state, mergeable, checks, unresolved review threads. Merged/closed: say so once. Green and clean: say ready to merge with its link. Needs a change: send to the worker on attempt 1 or 2, say a fix is starting, make this wait again with the next attempt. After attempt 2: say it still needs work, needs owner; no new wait. A request from someone not on your Who can ask: change nothing, tell your owner in this chat, make this wait again with the same attempt."
```

Start at attempt 1. Remove the wait when the owner says to stop watching:

```bash
orca automations list
orca automations remove <id>
```

### 4. Wait on one GitHub Actions run

Only when `trigger-options` lists `github.workflow_finished`. Dispatch with `gh workflow run`, then keep the run ID and immutable repository ID:

```bash
gh api --hostname github.com repos/<owner>/<repo> --jq "{id,full_name}"
orca automations create --bot <you> --name "Run <id>" --once \
  --by <expected finish plus margin> \
  --on "github.workflow_finished run=<link>" \
  --prompt "<run ID, immutable repo ID, exact --on rule, deadline instructions>"
```

Verify the saved repo ref names that same repository ID with `gh api --hostname github.com repositories/<repo-id> --jq .full_name`.

## Part C — answer where you were asked (Rule R5)

| Wake source | Where the answer goes |
|-------------|----------------------|
| Item mail | Comment on the item (`bot item comment <n>`), then NO_REPLY if nothing else needed |
| Chat / Slack / Linear / GitHub thread | Final message in that thread; never answer only with NO_REPLY |
| Item comment from owner | Comment on the item; if the question still stands, set it Needs you again |

## Completion

- `repo list` and `worktree ps` checked before any new worker.
- Each recurring request is one named automation in `orca automations list`; trigger-options confirmed the event exists.
- The answer's location matches the wake source (Rule R5).