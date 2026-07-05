#!/usr/bin/env python3
"""Behavioral smoke tests: does the constitution elicit honest,
conformant warrants from an LLM — including when honesty is the hard
answer?

Each directory under ci/cases/ is one canned dispatch with a known
honest outcome: task.md is the prompt, expect.json declares the
narrative (title / tests / honest_outcome) and the deterministic
grading (allowed STATUS values, required/forbidden content) on top of
the shape and per-family hard rules in validate_warrant.py. The model
gets the agent file body as its system prompt plus the case's
manifest and task inline (no tools in CI, so the skill is injected
rather than read).

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
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_warrant import validate, claim_number  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "ci" / "cases"
ENDPOINT = "https://models.github.ai/inference/chat/completions"
MODEL = os.environ.get("WO_MODEL", "meta/Llama-3.3-70B-Instruct")
ATTEMPTS = int(os.environ.get("WO_ATTEMPTS", "3"))
IN_ACTIONS = bool(os.environ.get("GITHUB_ACTIONS"))


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)


def group(title: str) -> None:
    print(f"::group::{title}" if IN_ACTIONS else f"\n▶ {title}")


def endgroup() -> None:
    print("::endgroup::" if IN_ACTIONS else "")


def complete(system: str, user: str, token: str) -> str:
    # The free tier rate-limits aggressively (429), especially the
    # Actions GITHUB_TOKEN; honor Retry-After instead of failing.
    for backoff in range(6):
        try:
            return _complete_once(system, user, token)
        except urllib.error.HTTPError as e:
            if e.code != 429 or backoff == 5:
                raise
            wait = min(int(e.headers.get("Retry-After") or 30), 120)
            print(f"  (rate-limited by the free tier, waiting {wait}s)")
            time.sleep(wait)


def _complete_once(system: str, user: str, token: str) -> str:
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


def claim_band_note(output: str, expect: dict) -> str | None:
    """Non-blocking reality check on the CLAIM number, where a case
    declares the band the formula implies."""
    band = expect.get("info_claim_band")
    if not band:
        return None
    value = claim_number(output)
    if value is None:
        return "no numeric CLAIM value found to check"
    ok = band["min"] <= value <= band["max"]
    verdict = "inside" if ok else "OUTSIDE"
    return (f"CLAIM says {value:g} {band['unit']} — {verdict} the "
            f"plausible band [{band['min']}, {band['max']}] "
            f"{band['unit']}. {band['note']}")


def run_case(case_dir: Path, system: str, token: str) -> dict:
    expect = json.loads((case_dir / "expect.json").read_text())
    manifest_id = expect["manifest"]
    manifest = (ROOT / "skills" / "claim-licensing" / "manifests" /
                f"{manifest_id}.md").read_text()
    task = (case_dir / "task.md").read_text()
    user = f"{task}\n\n--- MANIFEST ({manifest_id}) ---\n{manifest}"
    result = {"name": case_dir.name, "title": expect.get("title", ""),
              "passed": False, "attempt": None, "info": None}

    group(f"CASE {case_dir.name} — {expect.get('title', '')}")
    print(f"WHAT THIS TESTS: {expect.get('tests', '(not described)')}")
    print(f"HONEST OUTCOME REQUIRED: "
          f"{expect.get('honest_outcome', '(see expect.json)')}\n")

    for attempt in range(1, ATTEMPTS + 1):
        print(f"----- model output ({MODEL}, attempt "
              f"{attempt}/{ATTEMPTS}) -----")
        output = complete(system, user, token)
        print(output)
        print("----- end model output -----\n")

        problems = validate(output, manifest_id, expect)
        if not problems:
            result["passed"] = True
            result["attempt"] = attempt
            result["info"] = claim_band_note(output, expect)
            print(f"GRADING: conformant — the warrant meets every "
                  f"gate for this case.")
            if result["info"]:
                print(f"REALITY CHECK (non-blocking): {result['info']}")
            print(f"\n✅ CASE {case_dir.name}: PASS "
                  f"(attempt {attempt}/{ATTEMPTS})")
            endgroup()
            return result
        print(f"GRADING: attempt {attempt} rejected —")
        for p in problems:
            print(f"  ✗ {p}")
        print()

    print(f"❌ CASE {case_dir.name}: FAIL — no honest, conformant "
          f"warrant in {ATTEMPTS} attempts. The constitution did not "
          f"survive contact with this model on this case.")
    endgroup()
    return result


def write_job_summary(results: list[dict]) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    lines = [
        "## warrant-smoke — honesty cases against a free model",
        "",
        f"Model: `{MODEL}` · up to {ATTEMPTS} attempts per case · "
        "grading is deterministic (`ci/validate_warrant.py` + each "
        "case's `expect.json`)",
        "",
        "| Case | Verdict |",
        "|---|---|",
    ]
    for r in results:
        verdict = (f"✅ pass (attempt {r['attempt']}/{ATTEMPTS})"
                   if r["passed"] else "❌ fail")
        lines.append(f"| `{r['name']}` — {r['title']} | {verdict} |")
    infos = [r["info"] for r in results if r["info"]]
    if infos:
        lines += [""] + [f"> {i}" for i in infos]
    Path(path).open("a").write("\n".join(lines) + "\n")


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

    print("=" * 64)
    print("warrant-smoke: does the constitution survive contact "
          "with a model?")
    print(f"Each case below is a canned dispatch whose HONEST outcome "
          f"is known\nin advance. A free model ({MODEL}) gets the "
          "warrant-officer agent\nfile as its system prompt plus one "
          "manifest and one task, and must\nproduce a warrant that a "
          "deterministic grader accepts — including\nrefusing to "
          "license what cannot be licensed. Fluent prose that\ndodges "
          "honesty fails.")
    print("=" * 64)

    results = [run_case(d, system, token) for d in case_dirs]
    write_job_summary(results)

    failed = [r["name"] for r in results if not r["passed"]]
    print()
    if failed:
        print(f"RESULT: {len(failed)} of {len(results)} cases failed: "
              f"{failed}")
        sys.exit(1)
    print(f"RESULT: all {len(results)} cases passed — the "
          "constitution held, including where the honest answer was "
          "to refuse.")


if __name__ == "__main__":
    main()
