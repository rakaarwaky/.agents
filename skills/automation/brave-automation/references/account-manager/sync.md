# Sync — Profile Sync Chain Management

**Goal:** enroll source profiles into a Brave Sync Chain and join target profiles to the same chain.

## Workflow

1. **Verify browser flags**:
   - Ensure Brave is launched without `--disable-sync`. If `--disable-sync` is present, `brave://settings/braveSync` renders blank and all sync RPCs fail.

2. **Source profile chain setup**:
   - Navigate source profile to `brave://settings/braveSync/setup`.
   - If not enrolled, click `Start a new Sync Chain` -> `Computer`.
   - If an invalid/deleted chain message appears ("It looks like the sync chain you are on was deleted or is no longer valid"), click `Leave Sync Chain` or `Reset and re-join sync chain` and confirm the dialog before re-attempting setup.

3. **Mnemonic extraction**:
   - In the "Sync Chain Code" dialog, extract the 24/25-word phrase directly from the Shadow DOM `textarea.sync-code-text` (or `settings-brave-sync-code-dialog textarea`).
   - Do not parse the outer dialog or widget wrapper text, as UI buttons and status labels pollute the mnemonic string.

4. **Target profile joining**:
   - For each target profile, navigate to `brave://settings/braveSync/setup`.
   - Click `I have a Sync Code`.
   - Paste the extracted 24/25-word code into the input field and submit.
   - Wait for the profile to complete sync initialization.

5. **On-disk verification**:
   - Read `<profile_dir>/Preferences` JSON.
   - Inspect `brave_sync_v2.seed`. All profiles successfully joined to the same Sync Chain share the exact same seed string.

## Pitfalls & Lessons

- **Shadow DOM extraction**: Brave Settings uses Polymer Web Components. Document-level `document.querySelector` cannot pierce the dialog shadow roots; recursively traverse `element.shadowRoot` to find `textarea.sync-code-text`.
- **Stale chain lock**: A profile with a broken sync seed must explicitly execute the "Leave Sync Chain" flow. Joining a new code while a stale seed is recorded in `Preferences` without clearing it first will fail.
- **Process termination**: Always terminate Brave instances cleanly before reading/modifying profile preferences. Use targeted PIDs or `pkill -9 -x "brave"` / `pkill -9 -f "remote-debugging-port="` to avoid terminating caller scripts.
- **Strict profile roster**: Prune residual `Default` / `Personal` profiles so only profiles in `profile.csv` remain registered in `Local State`.