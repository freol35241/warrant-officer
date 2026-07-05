#!/usr/bin/env python3
"""Behavioral smoke tests: does the constitution elicit honest,
conformant warrants from an LLM — including when honesty is the hard
answer?

Each directory under ci/cases/ is one canned dispatch with a known
honest outcome: task.md is the prompt, expect.json declares the
deterministic grading (allowed STATUS values, required/forbidden
content) on top of the shape and per-family hard rules in
validate_warrant.py. The model gets the agent file body as its system
prompt plus the case's manifest and task inline (no tools in CI, so
the skill is injected rather than read).

Uses GitHub Models (free tier; GITHUB_TOKEN with `models: read` in
Actions, or `GITHUB_TOKEN=$(gh auth token)` locally). This tests
prompt robustness — that the dispositions and contract survive
contact with a model — not Claude Code's dispatch mechanics.

Env: GITHUB_TOKEN (required), WO_MODEL (optional; any model on
https://github.com/marketplace/models), WO_ATTEMPTS (optional,
default 3 — free-tier models occasionally truncate or drift, so one
conformant warrant out of N passes a case, while a broken prompt
still fails all attempts).
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_warrant import validate, claim_number  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "ci" / "cases"
ENDPOINT = "https://models.github.ai/inference/chat/completions"
MODEL = os.environ.get("WO_MODEL", "meta/Llama-3.3-70B-Instruct")
ATTEMPTS = int(os.environ.get("WO_ATTEMPTS", "3"))


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)


def complete(system: str, user: str, token: str) -> str:
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "max_tokens": 1500,
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.load(resp)
    return data["choices"][0]["message"]["content"]


def info_claim_band(output: str, expect: dict) -> None:
    band = expect.get("info_claim_band")
    if not band:
        return
    value = claim_number(output)
    if value is None:
        print("  [info] no numeric CLAIM value found")
        return
    ok = band["min"] <= value <= band["max"]
    print(f"  [info] CLAIM value {value:g} {band['unit']} — "
          f"{'inside' if ok else 'OUTSIDE'} the plausible band "
          f"[{band['min']}, {band['max']}] ({band['note']})")


def run_case(case_dir: Path, system: str, token: str) -> bool:
    expect = json.loads((case_dir / "expect.json").read_text())
    manifest_id = expect["manifest"]
    manifest = (ROOT / "skills" / "claim-licensing" / "manifests" /
                f"{manifest_id}.md").read_text()
    task = (case_dir / "task.md").read_text()
    user = f"{task}\n\n--- MANIFEST ({manifest_id}) ---\n{manifest}"

    for attempt in range(1, ATTEMPTS + 1):
        output = complete(system, user, token)
        print(f"--- case {case_dir.name}, model {MODEL}, "
              f"attempt {attempt}/{ATTEMPTS} ---\n{output}\n"
              f"--- end output ---")
        problems = validate(output, manifest_id, expect)
        if not problems:
            info_claim_band(output, expect)
            print(f"case {case_dir.name}: PASS\n")
            return True
        print(f"attempt {attempt}: non-conformant:")
        for p in problems:
            print(f"  - {p}")
        print()
    print(f"case {case_dir.name}: FAIL — no conformant warrant in "
          f"{ATTEMPTS} attempts\n")
    return False


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    system = strip_frontmatter(
        (ROOT / "agents" / "warrant-officer.md").read_text())

    case_dirs = sorted(d for d in CASES.iterdir() if d.is_dir())
    if not case_dirs:
        print("no cases found under ci/cases/", file=sys.stderr)
        sys.exit(1)

    failed = [d.name for d in case_dirs
              if not run_case(d, system, token)]
    if failed:
        print(f"SMOKE TESTS FAILED: {failed}")
        sys.exit(1)
    print(f"smoke tests: all {len(case_dirs)} cases passed")


if __name__ == "__main__":
    main()
