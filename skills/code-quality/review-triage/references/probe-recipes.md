# Probe Recipes

Proven probe patterns for common behavioral claim types in UX/code reviews. Each recipe is a Python one-liner or short script that executes the cited code path with a crafted input and asserts the observed output. Run these before classifying any claim that alleges runtime behavior.

## General pattern

```python
import sys
sys.path.insert(0, 'modules')
sys.path.insert(0, 'modules/<feature>/src')  # for capability imports

from <module> import <function_or_class>
# ... craft input, call, assert ...
```

## Parse→render data loss (UX-S5-001 class)

Construct a markdown string with hand-written prose inside a section, call `parse_memory_file` then `render_memory_file`, grep the output for the prose.

```python
from shared.src.memory.utility_memory_helper import parse_memory_file, render_memory_file

test_content = '''## Common Issues
### Testing
- missing edge case (seen 1 time)

This is a hand-written note that should be preserved.

## Recent Runs
This intro paragraph should survive.

### 2026-11-20 — "impl: test"
'''
state = parse_memory_file(test_content)
rendered = render_memory_file(state)
assert 'hand-written note' in rendered, 'DATA LOSS: note dropped'
assert 'intro paragraph' in rendered, 'DATA LOSS: intro dropped'
```

## Silent empty return on invalid input (UX-S5-003 class)

Call the function with `n=0` or `n=-5`, assert the result is empty with no exception.

```python
from shared.src.memory.utility_memory_helper import parse_memory_file, top_patterns

state = parse_memory_file('## Common Issues\n### Testing\n- test (seen 1 time)\n')
patterns, total = top_patterns(state, n=0)
assert patterns == [], f'Expected empty, got {patterns}'
assert total > 0, 'Total should be non-zero even when n=0'
# If no exception raised and patterns is empty → claim is valid
```

## Exception type that escapes (UX-S5-008 class)

Feed a file with invalid UTF-8 bytes to the reader, assert the exception type.

```python
import tempfile, os
from pathlib import Path
from unittest.mock import patch

with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as f:
    f.write(b'\xff\xfe\x00invalid')
    bad_file = f.name

try:
    with patch('capabilities_memory_reader.get_workspace_id', return_value='test-abc'):
        with patch('capabilities_memory_reader.memory_paths') as mock_paths:
            mock_paths.return_value = {'file': Path(bad_file)}
            reader = CapabilitiesReader()
            try:
                reader.read_content()
                print('FAIL: no exception raised')
            except UnicodeDecodeError:
                print('CONFIRMED: bare UnicodeDecodeError escapes')
            except MemoryHelperError:
                print('FIXED: wrapped in MemoryHelperError')
finally:
    os.unlink(bad_file)
```

## Non-git cwd fallback (UX-S1-002 class)

`chdir` to a non-git dir, call `memory_paths()`, catch the error, compare with `get_workspace_id()` in the same dir.

```python
import os, tempfile, subprocess

os.chdir('/tmp')  # or tempfile.mkdtemp()
# Verify not in a git repo
result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
assert result.returncode != 0, 'Must run outside a git repo'

from shared.src.memory.utility_memory_helper import memory_paths, get_workspace_id
from shared.src.common.taxonomy_sdc_error import WorkspaceIdError

# get_workspace_id has its own cwd fallback — should succeed
wid = get_workspace_id()

# memory_paths calls _repo_slug first — if it fails, check if fallback exists
try:
    p = memory_paths()
    print('PASS: cwd fallback works')
except WorkspaceIdError as e:
    print(f'CONFIRMED: no cwd fallback — {e}')
```

## Error message format (UX-S4-001, UX-S3-002, UX-S5-005 classes)

Call the function that raises, catch the exception, print `str(e)`, assert the claimed format is present.

```python
from capabilities_memory_writer import CapabilitiesWriter
from shared.src.common.taxonomy_sdc_error import SpecError

try:
    CapabilitiesWriter._validate_workflow({'description': 'no prefix'})
except SpecError as e:
    msg = str(e)
    if "(''" in msg:
        print('CONFIRMED: tuple repr in error message')
    if 'host:' in msg:
        print('CONFIRMED: embedded host: prefix')
    # Check for cause/retry/nothing-written in lock timeout
```

## Lock timeout message (UX-S5-005 class)

Acquire a lock, try to acquire it again, catch the timeout error.

```python
from shared.src.memory.utility_memory_helper import acquire_lock
from shared.src.common.taxonomy_sdc_error import LockTimeoutError
from pathlib import Path
import tempfile

with tempfile.TemporaryDirectory() as td:
    lock_path = Path(td) / 'test.lock'
    fd1 = acquire_lock(lock_path)
    try:
        acquire_lock(lock_path)
    except LockTimeoutError as e:
        msg = str(e)
        print(f'Message: {msg}')
        # Check for cause, retry, nothing-written
```

## Python version compatibility (UX-S1-001 class)

Check if a stdlib import requires a newer Python than the PRD floor. Don't try to run Python 3.9 — verify by checking the import against `sys.version_info` and the PRD statement.

```python
import sys
from datetime import UTC  # added in 3.11
print(f'Python: {sys.version_info[:2]}')
# Check PRD for floor: grep "Python 3" in PRD.md
# If floor is 3.9 and UTC is 3.11+ → claim is valid
```

## Quote deletion in merge (UX-S2-002 class)

Pass a description with embedded double quotes through `merge_recent_run`, inspect the stored description.

```python
from shared.src.memory.utility_memory_helper import merge_recent_run

state = {'header': [], 'common_issues': {}, 'recent_runs': []}
stats = {'categories_capped': {}, 'recent_runs_dropped': 0}
merge_recent_run(state, {'description': 'impl: handle "stale" lock'}, stats)
desc = state['recent_runs'][0]['description']
print(f'Stored: {desc}')
# Check if inner quotes are deleted or replaced
```

## Environment pitfalls

- `memory_paths()` succeeds inside any git repo (including `$HOME` if it's a git repo). To test the non-git path, `chdir` to `/tmp` or a `tempfile.mkdtemp()` and verify with `git rev-parse --show-toplevel` (rc 128) before running.
- The project `.venv` runs Python 3.14, not 3.9. `datetime.UTC` imports fine there. Confirm the Python floor by checking the import against `sys.version_info` and the PRD statement — not by running 3.9.
- Worktree tests need their own `.venv`: create with `python3 -m venv .venv && .venv/bin/pip install -q pytest ruff`, then run `PYTHONPATH=modules .venv/bin/python -m pytest modules/ -q -m "not dogfood"`.
- `pyproject.toml` with `[tool.ruff] target-version = "py39"` is needed when Grok uses `timezone.utc` instead of `datetime.UTC` — ruff's UP017 rule flags the latter on 3.11+ targets.