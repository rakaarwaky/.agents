# Step 4 — publish (draft-based repos only)

**Worktree rule:** the undraft/publish command itself runs from the Orca worktree where the release prep happened — never the main clone. The main clone stays clean.

Most repos (including the two watched ones) publish directly in Step 3's workflow — there is no separate draft/publish split, so Step 4 is a no-op for them. Proceed straight to [step-5-verify.md](step-5-verify.md).

For a repo that builds a **draft** release and needs a separate undraft step (e.g. a `softprops/action-gh-release` draft, or a registry that must be undrafted after build):

The publish step is irreversible and outward-facing. Proceed straight through:

```shell
gh release edit "$tag" --draft=false --latest -R <owner>/<repo>
```

Watch the publish job (~5–10 min):

```shell
gh run list --workflow=release.yml -R <owner>/<repo> --limit 1
gh run watch <run-id> -R <owner>/<repo> --exit-status
```

Recovery:

- Build job failed after publish: the release is now immutable. Delete the release *and* its tag, then re-run Step 3 with the same tag.
- Registry publish failed (transient / outage): artifacts are built; re-run just the failed job: `gh run rerun <run-id> --failed`.
- Wrong version already on the registry: versions cannot be reused or overwritten. Ship the next `N` — do not try to reuse the tag.

Note edits must happen *before* this — drafts are mutable, published releases are not. In the headless flow the notes come from the prep PR / changelog, not from this step.