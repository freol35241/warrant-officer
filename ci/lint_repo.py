#!/usr/bin/env python3
"""Deterministic structural checks on the constitution. No LLM.

Verifies that the agent file, skill, and manifests keep the shape the
system depends on, so prose edits can't silently break the contract.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def check_agent() -> None:
    p = ROOT / "agents" / "warrant-officer.md"
    if not p.exists():
        err("agents/warrant-officer.md missing")
        return
    text = p.read_text()

    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        err("agent file: missing YAML frontmatter")
    else:
        fm = m.group(1)
        for field in ("name:", "description:", "tools:"):
            if field not in fm:
                err(f"agent frontmatter missing '{field}'")
        if "name: warrant-officer" not in fm:
            err("agent frontmatter name must be 'warrant-officer'")

    # The seven dispositions, by their opening phrases
    dispositions = [
        "Price the job first",
        "Cheap yardstick before expensive compute",
        "Name the load-bearing assumption",
        "Cheapest sufficient method",
        "Break your own result",
        "License the claim or declare a dead-end",
        "Every claim carries a reconstruction pointer",
    ]
    for d in dispositions:
        if d not in text:
            err(f"agent file: disposition '{d}' missing")

    # The warrant contract fields
    for field in ("CLAIM:", "FOR:", "METHOD:", "ENVELOPE:",
                  "LOAD-BEARING:", "ERROR:", "FALSIFICATION:",
                  "STATUS:", "RECONSTRUCT:", "LICENSED-UNDER:"):
        if field not in text:
            err(f"agent file: warrant field '{field}' missing from "
                "output contract")


def check_skill_and_manifests() -> None:
    skill = ROOT / "skills" / "claim-licensing" / "SKILL.md"
    if not skill.exists():
        err("skills/claim-licensing/SKILL.md missing")
        return
    stext = skill.read_text()
    if not re.match(r"^---\n.*?name: claim-licensing.*?\n---\n",
                    stext, re.DOTALL):
        err("SKILL.md: frontmatter missing or name != claim-licensing")

    mdir = ROOT / "skills" / "claim-licensing" / "manifests"
    manifests = sorted(mdir.glob("*.md")) if mdir.exists() else []
    if not manifests:
        err("no manifests found")

    required_sections = ["## Error profile", "## Envelope",
                         "## Falsification menu", "## Honest-exit"]
    for man in manifests:
        mtext = man.read_text()
        for sec in required_sections:
            if sec not in mtext:
                err(f"{man.name}: missing section '{sec}'")
        # every manifest listed in the SKILL.md index
        if f"manifests/{man.name}" not in stext:
            err(f"{man.name}: not listed in SKILL.md manifest index")


def check_template() -> None:
    p = ROOT / "templates" / "CLAUDE.md"
    if not p.exists():
        err("templates/CLAUDE.md missing")
        return
    text = p.read_text()
    if "warrant-officer" not in text:
        err("template CLAUDE.md: no dispatch rule referencing "
            "warrant-officer")
    if "Price the job" not in text:
        err("template CLAUDE.md: pricing disposition missing")


def main() -> None:
    check_agent()
    check_skill_and_manifests()
    check_template()
    if ERRORS:
        print("LINT FAILED:")
        for e in ERRORS:
            print(f"  - {e}")
        sys.exit(1)
    print("lint: all structural checks passed")


if __name__ == "__main__":
    main()
