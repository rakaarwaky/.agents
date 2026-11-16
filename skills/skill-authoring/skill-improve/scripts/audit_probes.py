#!/usr/bin/env python3
"""Mechanical audit probes for one skill directory, a category tree, or a skills root.

Single job: run the grep-class checks that `sac lint` and the quality gate would run,
so an improve/create run is never blocked by a broken `sac` install.
Dependencies: Python 3.8+ standard library. PyYAML is used when importable;
otherwise a minimal frontmatter reader takes over (named fallback, not a failure).

Usage:
    python3 scripts/audit_probes.py <path> [<path> ...] [--gone old-a.md,old-b.md]

Exit codes:
    0  no findings
    1  findings printed (one line per finding)
    2  usage or path error
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Ceilings below are owned by SKILL.md Rules (parser limits, structure); they are
# repeated here only as the executable form of those rules, never as a new home.
MANDATORY_KEYS = ("name", "description", "when-to-use", "argument-hint")
NAME_MAX = 64          # Rules: Grok Build parser limits
TEXT_MAX = 1024        # Rules: Grok Build parser limits
BODY_MAX = 200         # Rules: Structure (~100-200 lines)
BODY_HEADINGS = ["Rules", "Routing"]  # Rules: Mandatory body shape
QUESTIONS = [
    ("what & why", r"what & why"),
    ("when & where", r"when & where"),
    ("who", r"\bwho\b"),
    ("from where", r"from where"),
    ("by what means", r"by what means"),
    ("how", r"\bhow\b"),
    ("how far", r"how far"),
    ("whether", r"\bwhether\b"),
    ("what kind", r"what kind"),
    ("how come", r"how come"),
]  # step-14-tenq-standard.md
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(#[^)]*)?\)")
RULE_REF_RE = re.compile(r"\bR(\d{1,3})\b")
RULE_ROW_RE = re.compile(r"^\|\s*R(\d{1,3})\s*\|", re.M)
CELL_SEP_RE = re.compile(r"(?<!\\)\|")  # escaped pipes are content, not delimiters
FENCE_RE = re.compile(r"^```.*?^```", re.M | re.S)
INLINE_CODE_RE = re.compile(r"`[^`]*`")
PLACEHOLDER_CHARS = set("*\\<>{}")  # illustrative targets, not real links


def read_frontmatter(text: str) -> tuple[dict, str, list[str]]:
    """Return (keys, body, problems). Falls back to a line reader without PyYAML."""
    if not text.startswith("---"):
        return {}, text, ["frontmatter: missing opening ---"]
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text, ["frontmatter: unclosed (second --- missing)"]
    raw = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            return {}, body, ["frontmatter: not a mapping"]
        return {k: "" if v is None else str(v) for k, v in data.items()}, body, []
    except ImportError:
        pass
    except Exception as exc:  # malformed YAML is a finding, not a crash
        return {}, body, [f"frontmatter: YAML parse error ({exc})"]
    keys: dict[str, str] = {}
    current = None
    block: list[str] = []
    for line in raw.splitlines():
        if current is not None:
            if line.startswith((" ", "\t")) or not line.strip():
                block.append(line.strip())
                continue
            keys[current] = " ".join(x for x in block if x)
            current, block = None, []
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value in (">-", ">", "|", "|-"):
            current, block = key, []
            continue
        keys[key] = value.strip("\"'")
    if current is not None:
        keys[current] = " ".join(x for x in block if x)
    return keys, body, []


def strip_fences(text: str) -> str:
    return FENCE_RE.sub("", text)


def probe_skill(skill_md: Path, gone: list[str]) -> list[str]:
    out: list[str] = []
    rel = skill_md.parent
    text = skill_md.read_text(encoding="utf-8")
    keys, body, problems = read_frontmatter(text)
    out += [f"{skill_md}: {p}" for p in problems]

    for key in MANDATORY_KEYS:
        if key not in keys:
            out.append(f"{skill_md}: mandatory key missing: {key}")
    if "triggers" in keys:
        out.append(f"{skill_md}: forbidden key present: triggers (use when-to-use)")
    name = keys.get("name", "")
    if name and name != rel.name:
        out.append(f"{skill_md}: name-mismatch: {name} != directory {rel.name}")
    if name and not NAME_RE.match(name):
        out.append(f"{skill_md}: name-format: {name}")
    if len(name) > NAME_MAX:
        out.append(f"{skill_md}: name over {NAME_MAX} chars")
    for key in ("description", "when-to-use"):
        value = keys.get(key, "")
        if len(value) > TEXT_MAX:
            out.append(f"{skill_md}: {key} over {TEXT_MAX} chars ({len(value)})")
    if re.search(r"[<>\"]", keys.get("description", "")):
        out.append(f"{skill_md}: description-characters: contains < > or quote")

    prose = strip_fences(body)
    titles = re.findall(r"^# (.+)$", prose, re.M)
    sections = re.findall(r"^## (.+)$", prose, re.M)
    if len(titles) != 1:
        out.append(f"{skill_md}: body shape: {len(titles)} '#' titles, expected 1")
    if sections != BODY_HEADINGS:
        out.append(f"{skill_md}: body shape: '## ' headings are {sections}, expected {BODY_HEADINGS}")
    if len(body.splitlines()) > BODY_MAX:
        out.append(f"{skill_md}: body over {BODY_MAX} lines ({len(body.splitlines())})")

    refs = sorted(p for p in (rel / "references").rglob("*.md")) if (rel / "references").is_dir() else []
    for ref in refs:
        if ref.name not in text:
            out.append(f"{skill_md}: reference-not-linked: references/{ref.relative_to(rel / 'references')}")

    rule_ids = set(RULE_ROW_RE.findall(text))
    for path in [skill_md, *refs, *sorted((rel / "template").rglob("*.md"))]:
        if not path.is_file():
            continue
        scan = strip_fences(path.read_text(encoding="utf-8"))
        links = INLINE_CODE_RE.sub("", scan)
        for target, _anchor in LINK_RE.findall(links):
            if target.startswith(("http://", "https://", "/")):
                continue
            if PLACEHOLDER_CHARS & set(target):
                continue
            if not (path.parent / target).resolve().is_file():
                out.append(f"{path}: dangling link: {target}")
        if path != skill_md:
            for rid in set(RULE_REF_RE.findall(scan)):
                if rid not in rule_ids:
                    out.append(f"{path}: unknown rule citation: R{rid} (not in {skill_md.name} Rules)")
        for old in gone:
            if old in scan:
                out.append(f"{path}: retired filename still referenced: {old}")

    for path in [skill_md, *refs]:
        expected = None
        for lineno, line in enumerate(strip_fences(path.read_text(encoding="utf-8")).splitlines(), 1):
            if line.startswith("|"):
                width = len(CELL_SEP_RE.findall(line))
                if expected is None:
                    expected = width
                elif width != expected:
                    out.append(f"{path}:{lineno}: broken table row: {width - 1} cells, expected {expected - 1} (escape literal pipes as \\|)")
            else:
                expected = None

    corpus = text + "\n".join(p.read_text(encoding="utf-8") for p in refs)
    for label, pattern in QUESTIONS:
        if not re.search(pattern, corpus, re.IGNORECASE):
            out.append(f"{skill_md}: core question unclaimed: {label}")
    return out


def collect(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        root = Path(raw)
        if not root.exists():
            raise FileNotFoundError(raw)
        if root.is_file() and root.name == "SKILL.md":
            found.append(root)
        elif root.is_dir():
            found.extend(sorted(root.rglob("SKILL.md")))
    return found


def main(argv: list[str]) -> int:
    gone: list[str] = []
    targets: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == "--gone":
            i += 1
            if i >= len(argv):
                print("usage error: --gone needs a comma-separated list", file=sys.stderr)
                return 2
            gone = [x.strip() for x in argv[i].split(",") if x.strip()]
        else:
            targets.append(argv[i])
        i += 1
    if not targets:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        skills = collect(targets)
    except (FileNotFoundError, OSError) as exc:
        print(f"path error: {exc}", file=sys.stderr)
        return 2
    if not skills:
        print(f"path error: no SKILL.md under {', '.join(targets)}", file=sys.stderr)
        return 2
    findings: list[str] = []
    for skill_md in skills:
        try:
            findings += probe_skill(skill_md, gone)
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(f"{skill_md}: unreadable ({exc})")
    for line in findings:
        print(f"FINDING {line}")
    print(f"probed {len(skills)} skill(s): {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
