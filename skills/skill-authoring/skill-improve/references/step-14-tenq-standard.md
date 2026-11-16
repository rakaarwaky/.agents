# Improve — Step 14: The quality standard and score gate

**Goal:** every target skill is scored against ten core questions, each score carries evidence, and the gate verdict is computed — not asserted.

`skill-improve` runs this on every target (`step-12-apply.md`); `skill-create` reads it at `../skill-create/references/step-2-drafting.md` and `step-6-write-skill.md`. Nothing else restates these numbers.

## The ten questions

Score the skill as an agent contract: what its own agent must know to run without guessing. For `skill-create` and `skill-improve` the answers describe the authoring run; the same ten questions are then enforced on every target skill they produce.

| Question | What a score-2 answer names | Single home in the target |
| --- | --- | --- |
| What & why | The one deliverable, plus a done-criterion that is a command or grep probe | Rules row (success metric) |
| When & where | Activation terms, plus the environment precondition (directory, file, or dependency that must exist) | Frontmatter `description:` / `when-to-use:`; precondition as a Rules row |
| Who | Audience of the output, plus language, tone, and conventions to follow | Rules row (audience & tone) |
| From where | The exact files, config, and user arguments read before acting | The step that reads them |
| By what means | Mandatory tools and commands, and forbidden ones | Rules row (tools); exact syntax in the using step |
| How | Numbered steps in execution order, each with a stop condition | Routing table + one step file per step |
| How far | Max files touched, max iterations before stopping, forbidden actions | Rules row (ceilings) |
| Whether | `IF <condition> -> <action or owning step>` branches | Routing row, or the owning step's branch table |
| What kind | Deliverable format and destination: paths written, report shape | Rules row (report shape) + the verify step |
| How come | Per failure: observed symptom, cause, exact recovery command | The failing step's fallback table |

Placement follows the information-distribution test (`step-10-information-distribution.md`): an answer read by more than one step lands in Rules; an answer read by exactly one step lands in that step file. A Rules row and a step file name the answers they cover in their Covers line; `—` means the row covers none.

## Scoring rubric

| Score | Criterion | Example (skill domain) |
| --- | --- | --- |
| 0 | Absent, or the answer restates the question | "Handle errors properly" |
| 1 | Present but not executable: a thing is named without a path, command, number, or step | "Read the relevant files", "do not touch too much" |
| 2 | Executable and verifiable: every noun resolves to a path, command, number, or named step | "Read `Cargo.toml` and `src/cli/mod.rs`; stop after 2 failed `cargo test` runs" |

**Guess test (applies to every score-2 claim):** read the answer as an instruction to a fresh agent. If any word requires a guess — relevant, appropriate, clean, reasonable, as needed, properly — the score is 1, not 2.

**Evidence rule:** every score cites `path:line` or a command whose output proves it. A score without evidence is scored 0.

## Gate arithmetic

- Total = sum of the ten scores; maximum 20.
- **PASS** = total ≥ 18 **and** no question scores 0 without an approved N/A.
- **N/A** is allowed only when the question genuinely cannot apply to the skill. It requires a one-line justification in the score block, it scores 0, and the divisor is never reduced. Consequence: at most one N/A per skill, and only when the other nine questions score 2.
- **FAIL** → run the patch cycle in `step-15-tenq-diagnosis.md`, then re-score. The cycle budget is 2 per skill per invocation.
- Budget exhausted and still below the gate → emit the score block with `Gate: FAIL` and the remaining gap list, and stop. Keep the edits already applied, keep the catalog consistent, and never report the skill as done, production-ready, or published.
- A draft answer sheet is scored with the same rubric before any file is written (`skill-create` step 2); an answer that never landed in a file scores 0 at artifact time.

## Score block

Emit this block verbatim in the run report, one block per skill. It is the required score section of the report (Rules: report shape).

```markdown
### Quality score — <skill-name>
| Question | Score | Evidence (path:line or command) | Gap / patch |
| --- | --- | --- | --- |
| What & why | <0-2> | <SKILL.md:R21 or references/step-6-verify.md:12> | <— or the patch applied> |
| ... | | | |
Total: <n>/20 · N/A: <none, or question + one-line justification> · Gate: <PASS|FAIL>
Cycles used: <0-2> · Remaining gaps: <none, or list>
```

## Mechanical probes

Presence is mechanical; the 0–2 score stays a judgment recorded with evidence.

```bash
# Coverage: every core question must appear in the skill's own prose.
grep -rnE 'what & why|when & where|who|from where|by what means|how far|whether|what kind|how come' SKILL.md references/ || echo "coverage gaps"
```

Run `python3 <skill-improve>/scripts/audit_probes.py <target-skill-dir>` for the coverage probe plus the structural probes (body shape, mandatory keys, unlinked references, dangling links, unresolved rule-ID citations). Exit 0 = no findings, 1 = findings listed, 2 = usage or path error. The script is the fallback gate when `sac lint` is unavailable (`step-12-apply.md`, SAC Lint Fallback).

## Completion

- Ten rows scored, each with `path:line` or command evidence; N/A justified in one line if used.
- Total, gate verdict, cycles used, and remaining gaps computed and emitted in the score block.
- Every question below 2 is routed to `step-15-tenq-diagnosis.md` with its owning home named.