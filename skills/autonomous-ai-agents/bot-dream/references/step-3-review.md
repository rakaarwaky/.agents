# Step 3: Review existing memory

## Read current state

1. `cat MEMORY.md` — current index
2. `ls memory/*.md` — existing topic files
3. For each topic file, read its content

## Classify each candidate fact

| Classification | Meaning | Action |
|---|---|---|
| **NEW** | Fact not in MEMORY.md | Add to MEMORY.md + memory/ |
| **UPDATE** | Fact in MEMORY.md but details changed | Update both files |
| **STALE** | Fact no longer true (replaced, retired) | Remove via `orca bot memory forget` |
| **KEEP** | Fact still accurate | No change |

## Removal

Stale facts are removed with `orca bot memory forget`:

```bash
orca bot memory forget --fact "<exact line from MEMORY.md>"
```

Do NOT edit MEMORY.md directly to remove a fact — Orca restores it at turn end unless removed through `forget`.