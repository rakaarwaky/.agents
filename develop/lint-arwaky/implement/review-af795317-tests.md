## Tests Review

### Verdict: PASS_WITH_NITS

### Issues (if any)
- [severity: nit] Unrelated pre-existing test failures observed during review (none caused by this Cargo.toml change):
  - `cargo nextest` is not installed in this environment, so the prescribed gate command
    `CARGO_INCREMENTAL=0 cargo nextest run --workspace --lib --tests -j 2` cannot run; the
    fallback `cargo test --workspace --lib --tests` was used instead.
  - `dispatcher-lint-arwaky` `unit_lockstep_classifier_helpers`::`capability_exposure_lockstep_pin`
    fails on the clean tree (verified with `git stash`): fixture `capability-literal` expects
    `true` but `exposes_capability_in_cargo_toml` returns `false` for one of the two mirrored
    copies (doc-rules vs structure-rules). This is a stale literal mismatch between the two
    peer copies that predates this change (present as of commit `e4afa141`).
  - `project-setup-lint-arwaky` `unit_project_setup_installer_adapter`::`failed_pip_retry_reports_retry_exit_code_not_first`
    fails in this environment because `pip` is not on PATH (`/usr/bin/python3` is present but
    no `pip` binary), so the subprocess call returns `No such file or directory` instead of an
    exit-code error. Fails identically with and without the Cargo.toml change (verified via
    `git stash`).
- [severity: nit] `homepage` key removal: no Rust source, fixture, or script in the repo
  references `homepage`, so its removal has no build/test impact. `cargo check`, clippy, and
  the test suite all pass without it.

### Notes
- Build result: PASS. `cargo check 2>&1 | tail -10` exits 0; `cargo build --release --bin
  lint-arwaky-cli` also succeeds (55s). The `[lints] workspace = true` addition to the root
  package `lint_arwaky-arwaky` resolves cleanly against the already-defined
  `[workspace.lints.rust]` / `[workspace.lints.clippy]` sections.
- Test result: PASS for this change. `CARGO_INCREMENTAL=0 cargo test --workspace --lib --tests
  -j 2` (fallback, nextest unavailable) runs the full suite; with a prebuilt
  `target/release/lint-arwaky-cli` (required by the dispatcher `regression_scan_modes`
  subprocess tests), all targets pass except the two pre-existing failures listed above
  (`capability_exposure_lockstep_pin`, `failed_pip_retry_reports_retry_exit_code_not_first`),
  both confirmed unrelated by stashing the Cargo.toml diff and reproducing on the clean tree.
- Clippy result: PASS. `cargo clippy --all-targets -- -D warnings` and
  `cargo clippy --workspace --all-targets -- -D warnings` both exit 0 with the `[lints]
  workspace = true` inheritance active. The three remaining cargo-manifest
  `unused_dependencies` warnings (`rand`, `rustsec`, `shared-common`) pre-exist the change
  (verified via `git stash`) and are not gated by `-D warnings` since they are emitted at
  the manifest/lint level, not as code lints.
- Changed files: `Cargo.toml` only. Diff: added `[lints] workspace = true` under the
  `[package]` section; removed `homepage = "https://github.com/rakaarwaky/lint-arwaky"`.
  No crate-level test or source file was touched.
- All 41 workspace member crates already carry `[lints] workspace = true`; this change only
  extends that inheritance to the root package, which is the correct and intended scope.
