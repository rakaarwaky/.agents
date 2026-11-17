---
name: brave-setup
description: Install the baa CLI, initialize its XDG workspace, verify prerequisites, and troubleshoot common Brave automation failures on Linux.
when-to-use: "Use when the user wants to install or repair the baa CLI and its prerequisites, initialize the XDG state/data workspace, resolve XDG path issues, or debug CDP connection failures, Local State locks, and Safe Storage key errors. Not for provisioning profiles (account-manager), importing credentials (password-manager), or Google session scripting."
argument-hint: "<install | init | doctor> [--dir PATH]"
created_by: curator
---

# Brave Setup (`baa init`)

You get the `baa` CLI running on a Linux host: install the CLI from the
`tools/` project, initialize the XDG workspace, and repair common failures.
Profile provisioning, credential import/export, and Google session scripting
belong to the sibling `account-manager` and `password-manager` skills.

## Rules

| ID | Rule | Why | Check |
|----|------|-----|-------|
| R1 | **Linux + Chromium only.** Confirm the host before running anything. | Unsupported platforms produce opaque errors. | `uname -s` returns `Linux`; Brave (native, Flatpak, or Snap) is installed. |
| R2 | **Never use `/tmp` for state.** Logs and sessions live under `$XDG_STATE_HOME/baa` and `$XDG_DATA_HOME/baa`; a reviewer must find output there. | XDG compliance; state survives across runs. | `baa init` output shows XDG paths; no writes to `/tmp`. |
| R3 | **One workspace per host.** `baa init` is idempotent; re-running it re-detects install paths without clobbering existing state. | Re-detection after a Brave move or upgrade. | `baa init` exits 0 and XDG dirs exist under `$XDG_STATE_HOME/baa`. |
| R4 | **Verify with `baa --help` and `baa profile list` after install/init.** A silent install that leaves the console script unresolvable is the main failure mode. | Catch drift between package install and CLI surface early. | Both commands print their trees; no `ModuleNotFoundError`. |

## Routing

| File | Purpose |
|------|---------|
| [`references/install.md`](references/install.md) | Install the `baa` CLI from the `tools/` project with `uv` and verify the console scripts. |
| [`references/init.md`](references/init.md) | Initialize the XDG state/data workspace and configure `profile.csv` / `passwords.csv`. |
| [`references/troubleshooting.md`](references/troubleshooting.md) | CDP connection failures, `Local State` locks, Safe Storage key rotation, XDG path issues. |
---
name: password-manager
description: "Import and export browser credentials as Chromium Password Manager CSVs via the baa CLI: import a CSV into the Login Data DBs, or export saved passwords back to CSV."
when-to-use: "Use when the user wants to import credentials from a CSV into local Brave/Chromium Login Data databases, or export saved browser passwords back to a CSV file. Not for headless scraping without profiles, non-Chromium browsers, or cloud password managers. Profile provisioning and Google session scripting belong to the sibling account-manager skill; setup and troubleshooting belong to brave-setup."
argument-hint: "<import | export> <path> [--profile <name>] [--csv FILE]"
created_by: curator
---

# Password Manager (`baa password`)

You move credentials between CSV files and each Brave profile's `Login Data`
SQLite database through the `baa` CLI. `import` feeds a CSV into Chromium's
native password stores; `export` pulls saved passwords back out. Setup and
troubleshooting belong to the sibling `brave-setup` skill; profile provisioning
belongs to the sibling `account-manager` skill.

## Rules

| ID | Rule | Why | Check |
|----|------|-----|-------|
| R1 | **Profiles must exist first.** Rows whose profile is not registered land nowhere. | Unregistered profiles have no `Login Data` DB to write to. | `baa profile list` shows every profile named in the CSV before import. |
| R2 | **Idempotent import.** Re-running with the same CSV upserts, no duplicate rows. | Safe to re-run after a failed import or key rotation. | `baa password import` exits 0; row count in `Login Data` matches the CSV. |
| R3 | **Safe Storage key is per-system.** The AES key encrypting `Login Data` rows can rotate after a Brave upgrade; re-import after rotation. | Stale key produces unreadable rows. | On a `DecryptionError` during import, re-run after the key stabilizes. |
| R4 | **Close Brave before import.** A running Brave instance locks the `Login Data` DB. | File-lock errors abort the import. | No `pgrep -a brave` hits, or `baa password import` retries cleanly. |

## Routing

| File | Purpose |
|------|---------|
| [`references/import.md`](references/import.md) | `import <path>` — import a Chromium Password Manager CSV into the `Login Data` DBs. |
| [`references/export.md`](references/export.md) | `export <path>` — export saved passwords from Brave into a CSV file. |



---
name: account-manager
description: "Manage Brave browser profiles and Google sessions via the baa CLI: create, list, verify, and reset isolated accounts, plus scripted Google login, logout, and session checks."
when-to-use: "Use when the user wants to create or manage local Brave/Chromium accounts, provision or verify isolated browser profiles from profile.csv, script Google login or logout in a named profile, or check a saved Google session. Not for headless scraping without profiles, non-Chromium browsers, or cloud password managers. Setup, credential import/export, and troubleshooting belong to the sibling brave-setup and password-manager skills."
argument-hint: "<list | create | login | logout> [subcommand] [NAMES] [--profile <name>] [--email <email>] [--password <password>] [--csv FILE]"
created_by: curator
---

# Account Manager (`baa account`)

You manage local Brave/Chromium accounts through the `baa` CLI: provision isolated
profiles from `profile.csv` into Chromium's `Local State`, verify what landed, and
script Google login, logout, and session checks per profile. Setup and
troubleshooting belong to the sibling `brave-setup` skill; credential import/export
belongs to the sibling `password-manager` skill.

## Rules

| ID | Rule | Why | Check |
|----|------|-----|-------|
| R1 | **Linux + Chromium only.** Confirm the host before running anything; the shared taxonomy raises on other platforms. | Unsupported platforms produce opaque errors. | `uname -s` returns `Linux`; Brave (native, Flatpak, or Snap) is installed. |
| R2 | **One profile per account.** Each account gets its own named profile; never mix sessions or credentials across profiles. | Cross-profile leakage defeats the isolation model. | Each account maps to one profile name; no shared session storage. |
| R3 | **`profile.csv` is the source of truth.** Edit the CSV, then run the matching `baa` subcommand — never hand-edit `Local State` directly. | Manual edits are error-prone and not reproducible. | All profile changes go through `baa profile ensure` / `create`. |
| R4 | **Verify after every write.** A silent success that leaves a profile unregistered is the main failure mode. | Catch drift between CSV and live Chromium state early. | `baa profile list` shows every expected name after create/reset. |
| R5 | **Google login first may trigger a challenge.** A fresh profile can hit an email-link or app-password verification (`SessionChallenge`); resolve it once manually, then re-run login. | Google flags unknown profiles; re-running after resolution succeeds. | `baa google session <name>` reports a valid session after `login`. |

## Routing

| File | Purpose |
|------|---------|
| [`references/create.md`](references/create.md) | `create` subcommand — provision one or more accounts from `profile.csv` with `--profile`, `--email`, `--password`. |
| [`references/list.md`](references/list.md) | `list` subcommand — show every registered profile and which `profile.csv` entries are missing. |
| [`references/google-login.md`](references/google-login.md) | `login` subcommand — Google login in a named profile with session persistence. |
| [`references/google-logout.md`](references/google-logout.md) | `logout` subcommand — drop the Google session for a profile. |
| [`references/sync.md`](references/sync.md) | Sync chain management — enroll source and join targets to a Brave Sync Chain, extract mnemonic codes, verify seeds on disk. |
| [`references/provider-auth.md`](references/provider-auth.md) | Provider auth — automate AI provider sign-in (Kilo Code, Cline, others) across Brave profiles with Google OAuth, passkey bypass, and challenge handling. |

