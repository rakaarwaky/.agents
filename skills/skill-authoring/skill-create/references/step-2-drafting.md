# Create — Step 2: Draft the answers

**Goal:** the agent answers all ten core questions itself from the invocation's job description and the repo, and writes a draft `SKILL.md` + `references/` (+ `template/` if needed) under the system temp directory. Nothing is written to the real skills directory yet.

## Draft location

Resolve the draft directory from the environment, never the repo tree:

```bash
DRAFT_DIR="${TMPDIR:-/tmp}/skill-create-draft-<skill-name>"
mkdir -p "$DRAFT_DIR"
```

`${TMPDIR:-/tmp}` is the Linux temp root (`/tmp` on this host). A repo-root `tmp/` pollutes the git tree, shows up in `git status`, and risks being committed by a later `git add -A` — so the draft lives outside the repository for the whole create run. Clean it up when the run ends (`rm -rf "$DRAFT_DIR"`).

## The ten questions 

The agent answers each one autonomously from the job description and the repo. The user is not asked unless a forcing condition below applies.


| #   | Question      | Asks                                                                     | Derived from                                              |
| --- | ------------- | ------------------------------------------------------------------------ | --------------------------------------------------------- |
| Q1  | WHAT & WHY    | Skill essence + goal + success metric (when the task is considered done) | Job description + one existing example of the artifact    |
| Q2  | WHEN & WHERE  | Activation trigger + operating environment                               | Job description + repo layout                             |
| Q3  | WHO           | Actor, output audience, language/tone                                    | Repo conventions                                          |
| Q4  | FROM WHERE    | Source data/raw material that must be read                               | Project config + one existing example of the artifact     |
| Q5  | BY WHAT MEANS | Mandatory and forbidden tools/library/command                            | Tools the repo already uses; new dependencies forbidden   |
| Q6  | HOW           | Numbered SOP, sequential, deterministic                                  | Existing pattern → write → register → check → report      |
| Q7  | HOW FAR       | Scope, maximum count, timeout, iteration ceiling                         | Job description; otherwise the agent sets explicit limits |
| Q8  | WHETHER       | Agent decision when encountering different conditions                    | Job description; otherwise stop-and-report branches       |
| Q9  | WHAT KIND     | Deliverable format + where it is saved/sent                              | Deliverable format + destination path                     |
| Q10 | HOW COME      | How the agent diagnoses failure + recovery plan (self-healing)           | Job description; otherwise stop-and-report on failure     |


## Forcing conditions — ask the user only when

The agent asks the user exactly one question, naming the missing fact and the question, only when one of these holds:

- The job description names **two different deliverables** (two WHATs) → stop and propose two skills, one per invocation.
- A fact **cannot be derived** from the job description or the repo → ask one question for that missing fact.
- A derived answer is **ambiguous** and cannot be resolved by reading the repo → ask one disambiguating question.

This is the only user prompt in the create run; every other step is autonomous (Rules: safety model).

## Drafting procedure

Split the work across two steps: this step (drafting) and step 3 (review), with the reviewer sending issues back to this step until it reports 0.

### Spawn drafter subagent

Spawn a drafter subagent with `spawn_subagent`. The drafter writes **only** to `$DRAFT_DIR` — never directly into the `skills/` folder yet.

Drafter prompt must include:

```
You are the drafter for a new skill.

Job description: <the user's job description>
Category: <resolved category from step 1>
Skill name: <resolved name from step 1>

Answer the ten core questions (Q1–Q10) autonomously from the job description and the repo. Each answer names paths, commands, numbers, or steps — no prose, no restated questions, no vague terms like "relevant", "appropriate", or "properly".

Write the draft artifacts to the draft directory resolved above (`$DRAFT_DIR`, e.g. `/tmp/skill-create-draft-<skill-name>/`):
- SKILL.md — body shape: # <Skill Name> / ## Rules / ## Routing, including frontmatter description: and when-to-use:
- references/ — supporting reference files, each linked from SKILL.md
- templates/ — only if the skill needs one, one file per skeleton the skill ships

Every answer lands at exactly one home:
- What & why → Rules row (success metric)
- When & where → frontmatter description:/when-to-use: + precondition Rules row
- Who → Rules row (audience & tone)
- From where → the step file that reads the inputs
- By what means → Rules row (tools) + exact syntax in the using step
- How → Routing table + one step file per step
- How far → Rules row (ceilings)
- Whether → Routing row or owning step's branch table
- What kind → Rules row (report shape) + verify step
- How come → failing step's fallback table

Log every defaulted fact as `assumed` in a scratch sheet.
Do NOT write to the skills/ folder. Write only under $DRAFT_DIR.
When done, report the files written under $DRAFT_DIR and the scratch sheet with assumed defaults.
```

Then proceed to step 3 (`step-3-review.md`) for the reviewer loop.

## Grounding

Before answering what-kind, by-what-means, and how, read the files the new skill will operate on (its config, one existing example of the artifact it produces). An answer invented without reading the repo scores 1 at best.

## Defaults

Anything the job description does not state is decided by the agent and logged as `assumed` in the scratch sheet. Never default to a wider scope.

## Completion

- The draft under `$DRAFT_DIR` holds ten answers, each at its assigned home, every default logged as `assumed`.
- `description:` names artifact + action in third person; `when-to-use:` carries every trigger phrase, synonym, and negative scope; the two fields share no phrase.
- The drafter reported the files written under `$DRAFT_DIR`.
- The run continues to step 3 (`step-3-review.md`).