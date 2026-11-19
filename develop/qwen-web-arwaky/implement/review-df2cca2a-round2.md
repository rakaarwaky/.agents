# Round-2 Re-review — boundary-git-root (impl df2cca2a)

## Issue 1 — FAIL (security bug not fixed)

**Verdict**: FAIL — `_find_git_root` can still return `/` when `/.git` exists.

**Evidence** (modules/shared/src/common/utility_folder_compiler.py:716-728):
```python
def _find_git_root(start: Path) -> Path | None:
    """Walk up from ``start`` to the filesystem root, stopping at a ``.git`` entry or the home directory.

    ``.git`` may be a directory (clone) or a file (worktree/submodule).
    """
    home = Path.home().resolve()

    for cand in (start.resolve(), *start.resolve().parents):
        if (cand / ".git").exists():
            return cand
        if cand == home or cand.parent == cand:
            return None
    return None
```

**Check order at each `cand`**: (1) `.git` exists → `return cand`; (2) `cand == home or cand.parent == cand` → `return None`. The filesystem-root check (`cand.parent == cand`) runs **after** the `.git` check at the same `cand`.

**Concrete trace**:
- (a) Path under `/tmp`, no `.git` anywhere, home=`/home/raka`: walk climbs `/tmp/...` → `/tmp` → `/`. At `/`: checks `/.git`.exists() first. If no `/.git`, then `cand.parent == cand` is true → returns `None`. ✓ (but only if `/.git` is absent)
- (b) Path whose ancestors contain `/.git` (simulate): at `cand == /`, `/.git`.exists() is true → **returns `/`**. ✗ This is the exact exfiltration bug — boundary becomes `/`, disabling import confinement.
- (c) Path inside home with `.git` at home dir: walk reaches `home`, finds `home/.git` exists → returns `home`. ✓ (correct, returns home as git root)

**Critical rule violated**: the `cand.parent == cand` (filesystem-root) check must fire **before** the `.git` check at that same `cand`, so `/.git` never gets returned. Current order is inverted.

**Remaining action**: Reorder the checks so the root/home stop fires before the `.git` check:
```python
for cand in (start.resolve(), *start.resolve().parents):
    if cand == home or cand.parent == cand:
        return None
    if (cand / ".git").exists():
        return cand
return None
```
Also add a test that pins `Path.home` to a non-ancestor of the tree (so the walk actually reaches `/`) and asserts the result is `None` and `!= Path("/")`, including a simulated `/.git` case if possible.

## Issue 2 — PASS

**Verdict**: PASS — `_find_git_root` uses the `for cand in (start, *start.parents)` idiom matching `_find_tsconfig` and `_find_crate_root`.

**Evidence** (modules/shared/src/common/utility_folder_compiler.py:723):
```python
for cand in (start.resolve(), *start.resolve().parents):
```
Matches `_find_tsconfig` (line 439): `for cand in (start, *start.parents):` and `_find_crate_root` (line 536): `for cand in (path, *path.parents):`. The `.resolve()` calls are an acceptable addition (start may not be absolute).

## Issue 3 — PASS

**Verdict**: PASS — no redundant `.resolve()`; `git_root` returned directly.

**Evidence** (modules/shared/src/common/utility_folder_compiler.py:756-758):
```python
git_root = _find_git_root(folder_path)
if git_root is not None:
    return git_root
```
`_find_git_root` already resolves `start` internally (`start.resolve()`), and `cand` values from `.parents` are resolved, so `git_root` is resolved. The redundant `.resolve()` from round 1 (line 751) is removed.

## Issue 4 — PARTIAL (tests present, but filesystem-root test is masked)

**Verdict**: PARTIAL — edge-case tests exist and the autouse fixture is hermetic, but the filesystem-root-stop test (4b) does not actually verify that `/` is never returned.

**Evidence** (modules/jobs/tests/unit_folder_compiler.py:505-515, autouse fixture):
```python
@pytest.fixture(autouse=True)
def _hermetic_home(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: (tmp_path / "fake_home").resolve()))
```

**4(a) no-git-ancestor returns None** — PASS: `test_find_git_root_none_no_git` (line 643) and `test_find_git_root_none_when_no_git_and_home_is_ancestor` (line 626). Both assert `_find_git_root(target) is None`.

**4(b) filesystem-root stop (never returns /)** — FAIL (masked): `test_find_git_root_stops_at_filesystem_root` (line 655):
```python
fake_home = tmp_path.resolve()
monkeypatch.setattr(Path, "home", classmethod(lambda cls: fake_home))
target = tmp_path / "sub" / "dir"
target.mkdir(parents=True)
result = _find_git_root(target)
assert result is None
assert result != Path("/")
```
This pins `home` to `tmp_path.resolve()` — which **IS an ancestor** of `tmp_path / "sub" / "dir"`. The walk stops at `cand == home` (i.e., `tmp_path`) **before** ever reaching `/`. The test passes because of the home-stop, not because of the filesystem-root stop. It masks the Issue-1 regression: if `/.git` existed and the root check were wrong, this test would still pass since the walk never reaches `/`. This is exactly the subtle bug the round-1 review warned about ("pinning home to tmp_path itself, which WOULD be an ancestor and fire the home-stop before the filesystem-root stop, masking the Issue-1 regression").

To actually test 4(b), `home` must be pinned to a directory that is **NOT** an ancestor of the test tree, so the walk climbs all the way to `/`; then assert `result is None` and `result != Path("/")`.

**4(c) .git dir found** — PASS: `test_find_git_root_returns_git_root` (line 635).
**4(d) .git file (worktree) found** — PASS: `test_find_git_root_git_file` (line 643) and `test_git_file_for_worktree` (line 582).
**4(e) target == git repo root** — PASS: `test_target_folder_is_git_repo_root` (line 676).
**4(f) existing tests hermetic via autouse fixture** — PASS: fixture pins home to `tmp_path / "fake_home"`, which is **not** an ancestor of test trees under `tmp_path`, so the home-stop never fires mid-walk for those trees. Hermetic regardless of CI state.

**Remaining action**: Fix `test_find_git_root_stops_at_filesystem_root` so `home` is pinned to a non-ancestor (e.g. a separate tmp_path sibling) and assert `result is None` and `result != Path("/")`. Optionally simulate `/.git` existing and assert still `None`.

## Issue 8 — PASS

**Verdict**: PASS — `collect_folder_files_with_imports` docstring documents precedence chain, any-importable-file warning (incl. credential files), and monorepo scoping via `QWEN_WORKSPACE_ROOT`.

**Evidence** (modules/shared/src/common/utility_folder_compiler.py:768-785):
```text
Default boundary precedence: explicit ``boundary_root`` >
``QWEN_WORKSPACE_ROOT`` env var > git repo root (when the scanned folder
lives inside one) > ``folder_path.parent``. When inside a git repo, **any
importable file** under the repo root linked from module files is pulled
into the compiled output — not just ``.md`` docs — so files like
``internal_keys.yaml`` or ``app_config.json`` that don't match
``_SECRET_KEYWORDS`` can be exfiltrated. Users compiling folders that
link to credential files should tighten the boundary via
``QWEN_WORKSPACE_ROOT``. In a monorepo with a single ``.git`` at the top,
compiling ``projects/A/src`` sets the boundary to the monorepo root, so
links into ``projects/B`` resolve; use ``QWEN_WORKSPACE_ROOT`` to scope
to one sub-project.
```
Covers precedence chain ✓, credential-file warning ✓, monorepo scoping ✓.

## Issue 9 — PASS

**Verdict**: PASS — `capabilities_folder_compiler.py` `boundary_root` docstring has the same content.

**Evidence** (modules/jobs/src/capabilities_folder_compiler.py:73-88):
```text
Default precedence: this parameter >
``QWEN_WORKSPACE_ROOT`` env var (matching the MCP workspace
boundary) > git repo root when the scanned folder lives
inside one ... > the scanned folder's parent.
Inside a git repo, **any** importable file under the repo
root linked from module files is pulled into the output —
not just ``.md`` docs. In a monorepo, compiling
``projects/A/src`` scopes to the monorepo root, so links
into ``projects/B`` resolve; set ``QWEN_WORKSPACE_ROOT`` to
tighten to a single sub-project.
```
Matches Issue 8 content ✓.

## Issue 10 — PASS

**Verdict**: PASS — covered by the Issue 8/9 docstrings (any-importable-file warning under git root, not just docs).

**Evidence**: Same as Issues 8 and 9 — both docstrings state "any importable file under the repo root linked from module files is pulled into the compiled output — not just `.md` docs."

## Issue 11 — PARTIAL

**Verdict**: PARTIAL — docstring is accurate in spirit but is two lines (not one) and does not describe the filesystem-root termination or the `None` return.

**Evidence** (modules/shared/src/common/utility_folder_compiler.py:717-721):
```python
"""Walk up from ``start`` to the filesystem root, stopping at a ``.git`` entry or the home directory.

``.git`` may be a directory (clone) or a file (worktree/submodule).
"""
```
The round-1 review asked for a **one-line** docstring matching `_find_tsconfig` ("Return the nearest ``tsconfig.json`` walking up from ``start``.") and `_find_crate_root` ("Return the nearest ancestor directory containing ``Cargo.toml``."). Current docstring is two paragraphs and omits that it returns `None` when no `.git` is found and never returns `/`. It's accurate about `.git` being a dir or file, but incomplete on termination.

**Remaining action**: Condense to a one-line docstring, e.g.:
```python
"""Return the nearest ancestor of ``start`` (or ``start`` itself) containing a ``.git`` entry (dir or file), or ``None`` if none exists before the home directory or filesystem root."""
```

## New issues (if any)

None introduced by the fixer beyond the incomplete Issue-1 fix and the masked Issue-4(b) test noted above. No regressions in existing behavior — all 52 tests pass.

## Summary

- Issue 1 (security): FAIL — root check runs after `.git` check; `/.git` still returns `/`.
- Issue 2 (for-loop idiom): PASS.
- Issue 3 (no redundant resolve): PASS.
- Issue 4 (tests): PARTIAL — edge cases covered, autouse fixture hermetic, but `test_find_git_root_stops_at_filesystem_root` pins home to an ancestor (`tmp_path`), masking the filesystem-root stop.
- Issue 8 (collect docstring): PASS.
- Issue 9 (boundary_root docstring): PASS.
- Issue 10 (any-importable warning): PASS.
- Issue 11 (_find_git_root docstring): PARTIAL — not one line, doesn't describe `None`/root termination.

**4 PASS, 2 FAIL, 2 PARTIAL**

**Overall: REQUEST-CHANGES**

The security bug (Issue 1) is not actually fixed: the filesystem-root check must be reordered to fire before the `.git` check. Issue 4(b)'s test must be unmasked so it genuinely exercises the root stop. Docstring for Issue 11 should be condensed to one line. Once those are corrected, re-run `modules/jobs/tests/unit_folder_compiler.py` and re-verify.
