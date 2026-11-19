## Simplicity Review

### Verdict: PASS

### Issues (if any)

- [nit] `repository` is still duplicated between `[workspace.package]` (line 56) and `[package]` (line 154) with the same value. Cargo does not warn about this, and fixing it would mean adding `repository.workspace = true` to `[package]` and dropping the literal from `[package]` — that is an out-of-scope change, not part of the two warnings under review. The current edit correctly leaves it untouched. Noted only for future cleanup.

### Notes

- **Minimality**: Both warnings have a single, canonical, minimal fix and the diff implements exactly those.
  - `cargo::missing_lints_inheritance` (warn by default) → fixed by `[lints]\nworkspace = true` (2 lines). Cargo's own `help:` text literally suggests this exact 2-line insertion. There is no smaller fix; the alternative of `cargo::missing_lints_inheritance = "allow"` would be a suppression, not a fix, and would silently disable the inheritance the other 38 member crates already use.
  - `cargo::redundant_homepage` (warn by default) → fixed by deleting the single `homepage = "..."` line (1 deletion). Cargo's `help:` says "consider removing `package.homepage`". The minimum possible change for this warning is one deletion. No smaller fix exists.

- **Consistency**: The `[lints]` placement is correct. Cargo `[lints]` is a top-level manifest table, the same level as `[package]`, `[lib]`, `[[bin]]`, `[dependencies]`. It is placed immediately after the `[package]` block and before `[lib]` in the root `Cargo.toml`, which matches the dominant placement across member crates (e.g. `crates/logging/Cargo.toml` places `[lints]` right after `[package]`; others place it after `[dependencies]`). Both placements are valid; this one is consistent with the majority.

- **No scope creep**: Confirmed via `git diff HEAD --numstat` → `3	1	Cargo.toml` and `--name-only` → `Cargo.toml` only. Exactly 3 insertions (`[lints]`, `workspace = true`, blank line) + 1 deletion (`homepage`). No other file, no unrelated edits, no reformatting.

- **Alternative approaches (homepage vs repository)**: Removing `homepage` is the correct choice, not `repository`:
  - `repository` is the more canonical / standard field — it is what crates.io, docs.rs, and the repo's own 38 member manifests all carry. `homepage` is optional and here pointed at the same GitHub URL, making it pure duplication.
  - Verified: zero member crates declare `homepage` (grep over `crates/**/Cargo.toml` returns nothing); all declare `repository` (39/39). `crates/cli-commands/Cargo.toml` even uses `repository.workspace = true`. The root package was the sole outlier, so deleting `homepage` restores consistency with the entire workspace.
  - Removing `repository` instead would be the wrong call: it would drop the only field the ecosystem actually reads and break the workspace-wide convention.

- **Verification**: `cargo check -p lint_arwaky-arwaky` after the change emits neither `missing_lints_inheritance` nor `redundant_homepage`. Pre-fix, both warnings reproduced exactly as described. The fix resolves the two warnings with no new warnings introduced.

- **Consistency gap left in place (intentional)**: `[package]` carries `repository` as a literal rather than inheriting from `[workspace.package]`, while `[workspace.package]` also defines it. This is pre-existing and unrelated to the two warnings; touching it would be scope creep. Flagged as a nit only.