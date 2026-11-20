# User Experience Review — implement-deep-clean-findings (0b9c3a95)

Reviewed strictly from the end-user POV: QoL, simplicity, minimal configuration, cognitive load, time efficiency, and actionable feedback.

---

### Issue 1 [User] — Severity: bug
- **File**: `modules/mcp/src/surface_mcp_command.py:110`
- **Description**: `vision_help(section=...)` now always returns the same single-sentence static text. The `section` parameter still attempts to split content on `\n## ` headings, but the static text contains no markdown headings, so any call with `section != "all"` returns `Section '{section}' not found. Available: all, image, video, workspace`. This is a regression: previously `vision_help(section="image")` etc. could surface topic-specific guidance from SKILL.md. Now the section argument is effectively dead and users get an unhelpful error string instead of guidance.
- **Suggestion**: Restore section-aware help. Either keep the static text as the default but include real `## image`, `## video`, `## workspace` sections so the section parameter works, or at minimum return the full static text (with a hint like "try 'vision_help()' for the overview") instead of a bare "not found" error when a section is requested.
- **Status**: open

---

### Issue 2 [User] — Severity: bug
- **File**: `modules/video/src/capabilities_video_understanding.py` (Finding 21) and `modules/system/src/capabilities_system_job.py` / `modules/shared/src/utility_status.py` (Finding 13)
- **Description**: The `VideoUnderstanding` result `sampling` dict lost `scene_changes` and `motion_events`, and `get_status()`/`vision_status()` lost the `video_processing` capability key (the shared `build_status_dict()` only emits `image_analysis` and `llm_vision`). Any downstream consumer (CLI output, MCP client, TUI status screen) reading those fields now gets a missing key / KeyError. The output shape changed without a migration path, which breaks integrations and surprises users who rely on those fields.
- **Suggestion**: Preserve the previous output shape: keep `scene_changes` and `motion_events` in the `sampling` dict (they can default to 0 / `None` where not computed), and keep `video_processing` in the capabilities dict produced by `build_status_dict()` so `get_status()` and `vision_status()` remain backward compatible.
- **Status**: open

---

### Issue 3 [User] — Severity: suggestion
- **File**: `modules/system/src/capabilities_system_job.py:27` (Finding 17)
- **Description**: `get_status()` now caches its result for 30 seconds (`_STATUS_TTL_S = 30.0`). A user who fixes a problem (e.g. starts the LLM endpoint, corrects a config value) and immediately re-runs `vision_status` or `status` will see stale data for up to 30 seconds. The `refresh()` method exists but is not exposed through any user-facing surface (CLI, MCP tool, or TUI screen), so the user has no way to force a fresh probe. This hides current state and wastes the user's time re-running a command that appears "stuck" on old data.
- **Suggestion**: Either shorten the TTL, add a `refresh`/`force` parameter to `get_status()` that surfaces through the MCP `vision_status` tool and CLI `status` command, or expose a `vision_refresh_status` MCP tool / TUI button. At minimum, document the 30s staleness window in the tool's description so users know why status may lag.
- **Status**: open

---

### Issue 4 [User] — Severity: suggestion
- **File**: `modules/shared/src/utility_config_handler.py` (Findings 10, 14)
- **Description**: Config precedence changed from "env var only fills in missing keys" (`setdefault`) to "env var always wins" (`resolve_config_value` returns env value immediately if set). A user who has a local config file with a preferred URL/model AND an environment variable set will now find their local config silently ignored. This surprises users who intentionally configured values in a file and expected them to take effect unless overridden explicitly. Also, `load_merged_config()` now always populates `external` with defaults (`url=DEFAULT_LLM_URL`, `api_key=""`, `model=""`), changing the shape of the returned config vs. before when external keys were absent.
- **Suggestion**: Make precedence explicit and least-surprising: document clearly that environment variables always override local config. Consider a warning/log when an env var overrides a locally configured value so the user isn't left wondering why their file edit had no effect. Keep the default `external` block only when no source provides values, to avoid surprising callers that check `if "external" in config`.
- **Status**: open

---

### Issue 5 [User] — Severity: suggestion
- **File**: `modules/shared/src/utility_config_handler.py` (Finding 16)
- **Description**: `load_merged_config()` is now cached at module level and only invalidated by programmatic writes through `save_user_config()`/`save_config()`. A user who edits their config file by hand (e.g. with a text editor) will not see the change until the process restarts, because the cache holds the stale in-memory copy. This breaks the expectation that editing a config file is immediately effective.
- **Suggestion**: Either check the file mtime/size before returning the cached copy (cheap invalidation on external edits), or document that config edits require a restart / `refresh`. A small mtime check is the more user-friendly option and preserves the "just works" expectation for hand-edited configs.
- **Status**: open

---

### Issue 6 [User] — Severity: suggestion
- **File**: `modules/mcp/src/surface_mcp_command.py:52` (Finding 20)
- **Description**: `_execute_in_process()` no longer catches exceptions into a structured `{"ok": False, "error": {"code": ..., "message": ...}}` JSON dict; exceptions now propagate to the MCP framework. MCP clients render raw exceptions differently (often as stack traces or opaque error messages) compared to the previous clean JSON error payload. Users lose a consistent, machine-readable error shape they could parse and act on.
- **Suggestion**: Restore a friendly structured error response on the MCP surface (matching the CLI's behavior of raising, but translating to a clear JSON error dict at the MCP boundary), so users get actionable, human-readable error messages instead of raw exception propagation.
- **Status**: open

---

### Issue 7 [User] — Severity: nit
- **File**: `modules/mcp/src/surface_mcp_command.py:110`
- **Description**: The new static `vision_help` text is a single sentence that only names three commands (`va init`, `va image --image PATH`, `va video --video PATH`). It gives no guidance on what each command does, what arguments they take, or what to do when analysis fails. New users get minimal orientation and no actionable next steps when something goes wrong.
- **Suggestion**: Expand the static help text into a concise, scannable overview with one line per command and a "troubleshooting" pointer (e.g. "run `va status` to check dependencies"). This keeps it short but makes it genuinely actionable for first-time users.
- **Status**: open

---

## What's good for the user (QoL wins)

- **Finding 12** (`set_config` returns `key_str` instead of a `ConfigKey` object): Better user-facing output — the config key is now a plain string, cleaner and more readable.
- **Finding 9** (single `VideoCapture` handle reused for metadata + frame extraction): Faster video analysis, less redundant file opening — a real time saving.
- **Finding 11** (`mimetypes.guess_type` for image MIME): Correct MIME detection for more file types (e.g. `.webp`, `.tiff`) instead of assuming everything non-jpg is PNG — fewer failed uploads.
- **Finding 8** (cached `requests.Session`): Reduces connection overhead on repeated LLM calls — modest speed improvement.
- **Finding 18** (XDG cache dir for models): Follows platform conventions instead of hardcoding `~/.cache/vision-arwaky/models` — more correct, less surprising.

## Summary

The changes are mostly internal cleanups with positive speed/correctness effects, but there are four user-facing regressions to fix before shipping: the dead `vision_help(section=...)` argument, the changed `sampling`/`capabilities` output shape, the 30s status cache with no user-facing refresh, and the env-var-always-wins config precedence that can silently override local config files. Addressing these keeps the feature zero-friction and backward-compatible for existing users.
