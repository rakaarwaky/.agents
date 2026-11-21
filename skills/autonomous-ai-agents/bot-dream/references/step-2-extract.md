# Step 2: Extract durable facts

## Extraction rules

From each conversation, extract facts that meet all three criteria:

1. **Durable** — remains true across sessions and repos.
2. **Specific** — names a concrete thing (file path, field name, command, ownership rule).
3. **Not already in memory** — checked against existing `MEMORY.md` and `memory/*.md`.

## Format

Each candidate fact becomes one line for `MEMORY.md`:

```
- YYYY-MM-DD <one-line summary>. See memory/<topic>.md.
```

And one entry in `memory/<topic>.md` with full detail.

## Topic assignment

Pick the `memory/<topic>.md` file from this set (create new if none fit):

- `repo-json-schema.md` — repo.json structure and field values
- `setup-lane.md` — pr-babysit setup steps
- `templates.md` — skill templates
- `release-lane.md` — Risa-AutoRelease release workflow
- `auto-undraft.md` — confirmed auto-merge behaviors
- Other topic if the fact does not fit any of the above