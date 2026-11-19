---
name: brave-automation
description: "Install the baa CLI, manage Brave browser profiles and Google sessions, and import/export Chromium credentials as CSVs via the baa CLI on Linux."
when-to-use: "Use when the user wants to install or repair the baa CLI and its XDG workspace, provision or verify isolated Brave profiles from profile.csv, script Google login or logout per profile, check a saved Google session, import credentials from a CSV into Login Data DBs, export saved passwords back to a CSV, enroll profiles in a Brave Sync Chain, or automate AI provider sign-in (Kilo Code, Cline, Antigravity) across Brave profiles. Not for headless scraping without profiles, non-Chromium browsers, cloud password managers, or non-Linux hosts."
argument-hint: "<setup|password|account> <task>"
---

# Brave Automation (`baa`)

You get the `baa` CLI running on a Linux host and use it to provision isolated
Brave profiles, script Google auth, manage credentials as Chromium Password
Manager CSVs, and automate provider sign-in across profiles. The skill covers
three capability areas through one CLI surface:

- **brave-setup** — install the CLI, initialize the XDG workspace, repair failures.
- **password-manager** — import/export credentials as Chromium Password Manager CSVs.
- **account-manager** — provision profiles, script Google login/logout, manage sync chains, automate provider auth.

## Rules

| ID | Rule | Why | Check |
|----|------|-----|-------|
| R1 | **Linux + Chromium only.** Confirm the host before running anything; the shared taxonomy raises on other platforms. | Unsupported platforms produce opaque errors. | `uname -s` returns `Linux`; Brave (native, Flatpak, or Snap) is installed. |
| R2 | **Never use `/tmp` for state.** Logs and sessions live under `$XDG_STATE_HOME/baa` and `$XDG_DATA_HOME/baa`. | XDG compliance; state survives across runs. | `baa init` output shows XDG paths; no writes to `/tmp`. |
| R3 | **One workspace per host.** `baa init` is idempotent; re-running re-detects install paths without clobbering state. | Re-detection after a Brave move or upgrade. | `baa init` exits 0 and XDG dirs exist under `$XDG_STATE_HOME/baa`. |
| R4 | **`profile.csv` is the source of truth for profiles.** Edit the CSV, then run `baa profile ensure` — never hand-edit `Local State` directly. | Manual edits are error-prone and not reproducible. | All profile changes go through `baa profile ensure`. |
| R5 | **One profile per account.** Each account gets its own named profile; never mix sessions or credentials across profiles. | Cross-profile leakage defeats the isolation model. | Each account maps to one profile name; no shared session storage. |
| R6 | **Close Brave before import or profile writes.** A running Brave instance locks the `Login Data` and `Local State` DBs. | File-lock errors abort the import or profile ensure. | No `pgrep -a brave` hits, or the command retries cleanly. |
| R7 | **Safe Storage key is per-system.** The AES key encrypting `Login Data` rows can rotate after a Brave upgrade; re-import after rotation. | Stale key produces unreadable rows. | On a `DecryptionError`, re-run `baa password import` after the key stabilizes. |
| R8 | **Verify after every write.** A silent success that leaves a profile unregistered or a session stale is the main failure mode. | Catch drift between CSV and live Chromium state early. | `baa profile list` shows every expected name; `baa google session` reports expected state. |
| R9 | **Google login on a fresh profile may trigger a challenge.** Resolve the `SessionChallenge` (email link or app password) once manually, then re-run login. | Google flags unknown profiles; re-running after resolution succeeds. | `baa google session <name>` reports a valid session after `login`. |
| R10 | **Install verifies the CLI surface.** A silent install that leaves `baa` unresolvable is the install failure mode. | Catch drift between package install and CLI surface early. | `baa --help` and `baa profile list` print their trees; no `ModuleNotFoundError`. |
| R11 | **Success metric.** Every invocation ends with a verified state: `baa --help` resolves, `baa profile list` matches `profile.csv`, `baa google session` reports the expected session state, or the CSV row count matches `Login Data`. | The agent stops only when the probe passes. | Run the probe named in the active reference file's `## Completion` block; stop on pass, report on fail. |
| R12 | **Scope ceiling.** Max 12 files touched per invocation (one reference file plus the CSV it consumes). Max 3 repair iterations per failing check. Forbidden: editing files outside `skills/automation/brave-automation/`, deleting `profile.csv` or `passwords.csv` rows without archiving, running `baa` as `sudo`, modifying Brave's `Local State` outside `baa`. | Agents do not drift or loop. | `git diff --name-only` is a subset of the skill directory; iteration count ≤ 3. |
| R13 | **Failure fallback.** On `cdp connect timeout` -> confirm Brave is installed and `baa init` has run (`references/brave-setup/troubleshooting.md`). On `database is locked` -> close Brave (`pkill -f brave`) and re-run. On `DecryptionError` -> wait for Safe Storage key to stabilize, then re-import. On `SessionChallenge` -> resolve manually, then re-run login. On `FileNotFoundError` -> confirm Brave install path, re-run `baa init`. | Each named cause has a concrete recovery path. | The agent names the cause and runs the matching recovery command; it does not retry blindly. |

## Routing

| File | Purpose |
|------|---------|
| [`references/brave-setup/install.md`](references/brave-setup/install.md) | Install the `baa` CLI from the `tools/` project with `uv` and verify the console scripts. |
| [`references/brave-setup/init.md`](references/brave-setup/init.md) | Initialize the XDG state/data workspace and configure `profile.csv` / `passwords.csv`. |
| [`references/brave-setup/troubleshooting.md`](references/brave-setup/troubleshooting.md) | CDP connection failures, `Local State` locks, Safe Storage key rotation, XDG path issues. |
| [`references/password-manager/import.md`](references/password-manager/import.md) | `baa password import` — import a Chromium Password Manager CSV into the `Login Data` DBs. |
| [`references/password-manager/export.md`](references/password-manager/export.md) | `baa password export` — export saved passwords from Brave into a CSV file. |
| [`references/account-manager/create.md`](references/account-manager/create.md) | `baa profile ensure` — provision one or more accounts from `profile.csv`. |
| [`references/account-manager/list.md`](references/account-manager/list.md) | `baa profile list` — show every registered profile and flag missing CSV entries. |
| [`references/account-manager/google-login.md`](references/account-manager/google-login.md) | `baa google login` — Google login in a named profile with session persistence. |
| [`references/account-manager/google-logout.md`](references/account-manager/google-logout.md) | `baa google logout` — drop the Google session for a profile. |
| [`references/account-manager/sync.md`](references/account-manager/sync.md) | Sync chain management — enroll source and join targets to a Brave Sync Chain, extract mnemonic codes, verify seeds on disk. |
| [`references/account-manager/provider-auth.md`](references/account-manager/provider-auth.md) | Provider auth — automate AI provider sign-in (Kilo Code, Cline, Antigravity) across Brave profiles with Google OAuth, passkey bypass, and challenge handling. |