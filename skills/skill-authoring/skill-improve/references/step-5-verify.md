# Improve — Step 5: Verify and report

**Goal:** mechanically verify the improved skill and end with one report carrying the gate verdict.

## SAC lint fallback

When `sac lint` is unavailable (missing `modules/` → `ModuleNotFoundError: No module named 'cli'`, skills-root path error, or broken install), do not block the improve run. Run the equivalent grep-class checks directly: body shape (`grep -n '^#' <SKILL.md>`), frontmatter scan for four mandatory keys, description/when-to-use char-count against 1,024, unlinked-refs probe (`ls references/ | while read f; do grep -q "$f" SKILL.md || echo "unlinked: $f"; done`), and dangling-ref sweep (`grep -r "old-name"`). Report the fallback explicitly — a broken lint gate is an infra defect, not a blocker.

A broken `sac` CLI blocks both `sac lint` and `sac catalog --build`; the catalog rebuild falls back to `git add skills/catalog.json && git commit` if stale — state the missing rebuild in the report; do not block the run.

## Verify and report

1. `sac lint` passes (whole pack or scoped: `sac lint --category <name>`).
2. Pre-publish checklist (`step-3-publish.md`) fully checked.
3. `sac read <name>` — confirm frontmatter and body landed correctly.
4. Body shape verified mechanically: `grep -n '^#' <SKILL.md>` returns only `# Title` and exactly `## Rules`, `## Routing`.
5. Every sibling mention and cross-skill link names a skill that exists in the tree.
6. `sac catalog --build` run so `skills/catalog.json` reflects current frontmatter — a stale catalog is a publish defect.
7. `git log --oneline -4` and `git status` checked for parallel agent commits; staged set contains only this run's files plus `catalog.json`.
8. After commit, `git show --stat <sha>` must list exactly this run's files.

## TenQ standard — quality score and gate

Score each target skill against ten core questions (0–2 rubric):

| Question | Score-2 names |
|----------|---------------|
| What & why | One deliverable + done-criterion that is a command or grep probe |
| When & where | Activation terms + environment precondition |
| Who | Audience + language, tone, conventions |
| From where | Exact files, config, user arguments read before acting |
| By what means | Mandatory tools/commands + forbidden ones |
| How | Numbered steps in execution order, each with stop condition |
| How far | Max files touched, max iterations, forbidden actions |
| Whether | `IF <condition> -> <action or owning step>` branches |
| What kind | Deliverable format and destination |
| How come | Per failure: symptom, cause, exact recovery command |

**Score block** (emit verbatim, one per skill):

```markdown
### Quality score — <skill-name>
| Question | Score | Evidence (path:line or command) | Gap / patch |
| --- | --- | --- | --- |
| What & why | <0-2> | <SKILL.md:R21 or references/step-N-verify.md:12> | <— or patch applied> |
Total: <n>/20 · N/A: <none or question + justification> · Gate: <PASS|FAIL>
Cycles used: <0-2> · Remaining gaps: <none or list>
```

**Gate arithmetic:**
- Total = sum of ten scores; maximum 20.
- **PASS** = total ≥ 18 **and** no question scores 0 without an approved N/A.
- **N/A** allowed only when the question genuinely cannot apply. Requires one-line justification in score block, scores 0, divisor never reduced. At most one N/A per skill, and only when other nine score 2.
- **FAIL** → run patch cycle (below), re-score. Cycle budget is 2 per skill per invocation.
- Budget exhausted and still below gate → emit score block with `Gate: FAIL` and remaining gap list; stop. Keep edits applied, keep catalog consistent, never report skill as done/production-ready/published.

**Mechanical probes:**
```bash
grep -rnE 'what & why|when & where|who|from where|by what means|how far|whether|what kind|how come' SKILL.md references/ || echo "coverage gaps"
```

## TenQ diagnosis and patch cycle

Symptom → gap map:

| Symptom | Gap | Patch owner |
|---------|-----|-------------|
| Skill never triggers | When & where | Frontmatter |
| Skill triggers on wrong tasks | When & where | `when-to-use:` negative scope |
| Agent asks basic questions back | What & why, From where | Rules success-metric row + gathering step |
| Agent edits wrong files | When & where, How far | Rules ceilings row |
| Agent installs dependencies unasked | By what means | Rules tools row (forbidden clause) |
| Agent loops without stopping | How far, What & why | Rules ceilings row + success metric |
| Agent stuck when command fails | Whether, How come | Failing step's branch and fallback tables |
| Output format wrong | What kind | Rules report-shape row + verify step |
| Tone/language drifts | Who | Rules audience & tone row |
| Result correct but useless | What & why | Success metric measures wrong outcome |
| Agent deletes/damages work | How far | Forbidden-actions clause; archive-before-destroy |
| `sac lint` reports `reference-not-linked` | How | Routing table row for orphaned reference |
| Retired flag still governs a step | Whether | Rules safety-model row + every step mentioning flag |
| Two files state same fact | How | Losing copy; keep owner per info distribution test |

**Cycle (run once per failing question set, not once per question):**

1. **OBSERVE** — record symptom verbatim and the invocation that produced it. No symptom, no patch.
2. **MAP** — pick the row; write down the question and owning home before opening an editor.
3. **PATCH** — edit only that home. Step file owner → never edit body; Rules owner → never restate in step.
4. **REGRESS** — re-run happy path, edge case, deliberate error (missing precondition or failing check command). Re-run `sac lint` and coverage probe.
5. **RE-SCORE** — score patched questions with evidence, recompute gate. No `version:` key (parser ignores it; version record is commit message + report change list).

**Stop conditions:**
- Budget exhausted → emit remaining gap list with owning home for each; stop. Do not claim done.
- Patch would touch skill outside resolved scope → do not apply; report as out-of-scope finding.
- Same question fails same way twice → diagnosis was wrong; re-map from symptom table instead of retrying same edit.

## Completion

- Every lint rule fired is fixed or reported out of scope.
- Pre-publish checklist fully checked; every gap listed with owning file.
- `catalog.json` rebuilt; `git show --stat` lists exactly this run's files.
- One quality score block per target in report with total, verdict, cycles used, remaining gaps; FAIL verdict stated as FAIL.
- `--dry-run` emits the same report from the draft and writes nothing.
