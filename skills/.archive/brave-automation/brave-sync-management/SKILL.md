---
name: brave-sync-management
description: "Manage Brave Sync chains and profile enrollment."
when-to-use: "Use when synchronizing Brave profiles to a single Brave Sync Chain, extracting sync mnemonic codes, joining profiles, or troubleshooting sync enrollment and stale chain errors."
---

# Brave Sync Management

Manage Brave browser profile synchronization across multiple local profiles using the Brave Sync v2 protocol.

## When to Use
Use when synchronizing Brave profiles into a single shared Sync Chain, extracting sync mnemonic codes, joining profiles, or troubleshooting sync enrollment and stale chain errors.

## Workflow

1. **Verify Browser Flags**:
   - Ensure Brave is launched without `--disable-sync`. If `--disable-sync` is present, `brave://settings/braveSync` renders blank and all sync RPCs fail.

2. **Source Profile Chain Setup**:
   - Navigate source profile to `brave://settings/braveSync/setup`.
   - If not enrolled, click `Start a new Sync Chain` -> `Computer`.
   - If an invalid/deleted chain message appears ("It looks like the sync chain you are on was deleted or is no longer valid"), click `Leave Sync Chain` or `Reset and re-join sync chain` and confirm the dialog before re-attempting setup.

3. **Mnemonic Extraction**:
   - In the "Sync Chain Code" dialog, extract the 24/25-word phrase directly from the Shadow DOM `textarea.sync-code-text` (or `settings-brave-sync-code-dialog textarea`).
   - Do not parse the outer dialog or widget wrapper text, as UI buttons and status labels pollute the mnemonic string.

4. **Target Profile Joining**:
   - For each target profile, navigate to `brave://settings/braveSync/setup`.
   - Click `I have a Sync Code`.
   - Paste the extracted 24/25-word code into the input field and submit.
   - Wait for the profile to complete sync initialization.

5. **On-Disk Verification**:
   - Read `<profile_dir>/Preferences` JSON.
   - Inspect `brave_sync_v2.seed`. All profiles successfully joined to the same Sync Chain share the exact same seed string.

## Pitfalls & Lessons

- **Shadow DOM Extraction**: Brave Settings uses Polymer Web Components. Document-level `document.querySelector` cannot pierce the dialog shadow roots; recursively traverse `element.shadowRoot` to find `textarea.sync-code-text`.
- **Stale Chain Lock**: A profile with a broken sync seed must explicitly execute the "Leave Sync Chain" flow. Joining a new code while a stale seed is recorded in `Preferences` without clearing it first will fail.
- **Process Termination**: Always terminate Brave instances cleanly before reading/modifying profile preferences. Use targeted PIDs or `pkill -9 -x "brave"` / `pkill -9 -f "remote-debugging-port="` to avoid terminating caller scripts.
- **Strict Profile Roster**: Prune residual `Default` / `Personal` profiles so only profiles in `profile.csv` remain registered in `Local State`.
