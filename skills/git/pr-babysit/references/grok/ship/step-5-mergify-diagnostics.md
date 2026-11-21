# Step 5 — Mergify CI Diagnostics

Run when `MERGIFY_AVAILABLE` is `"configured"` and CI is still red after the fix pass. Provides deeper failure analysis before reporting back to Hermes.

## 1. Mergify events (queue history)

```bash
mergify events --pr <number> --since 7d --json 2>/dev/null
```

Look for:
- `action.queue.leave` with `merged: false` → dequeued; `dequeue_code` explains why
- `action.queue.checks_end` with `aborted: true` → checks interrupted; PR **stays queued** — do NOT treat as dequeue
- Multiple `command.queue` events → PR has been requeued before

## 2. Flaky-test quarantine

If the same test name has failed in multiple fix passes, it may be flaky:

```bash
mergify tests show -r <OWNER_REPO> '<test_name>' --json 2>/dev/null
```

If success ratio < 80% and the failure is intermittent:

```bash
# Suggest quarantine
echo "Test '<test_name>' looks flaky (<ratio>% success). Quarantine?"
```

On approval:

```bash
mergify tests quarantines add -r <OWNER_REPO> \
  --reason "flaky — quarantined by pr-babysit during PR #<number>" \
  '<test_name>'
```

After quarantining, re-process JUnit if available:

```bash
mergify ci junit-process <junit_xml_path> 2>/dev/null
```

## 3. JUnit upload (best-effort)

When JUnit XML artifacts are in the CI logs:

```bash
gh api "repos/$OWNER_REPO/actions/runs/<run_id>/artifacts" \
  --jq '.artifacts[] | select(.name | test("junit|test-results|report")) | .archive_download_url' \
  | head -1 | xargs -I{} curl -sL -H "Authorization: token $(gh auth token)" {} -o /tmp/junit.zip

unzip -o /tmp/junit.zip -d /tmp/junit-results 2>/dev/null
mergify ci junit-process /tmp/junit-results/*.xml 2>/dev/null
```

Upload failure does not block the pipeline.

## 4. Scope detection (informational)

```bash
mergify ci scopes --config .github/workflows/mergify.yml 2>/dev/null
```

Include affected scopes in the report.

## Report to Hermes

> **Mergify diagnostics:**
> - Queue history: <N> cycle(s) in last 7d
> - Flaky tests: <list or "none">
> - CI Insights: <uploaded / not available>
> - Affected scopes: <list or "not configured">
