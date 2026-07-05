#!/usr/bin/env python3
"""Behavioral smoke test: does the constitution elicit a conformant
warrant from an LLM?

Uses GitHub Models (free tier; GITHUB_TOKEN with `models: read` in
Actions, or a PAT locally). The model gets the agent file body as its
system prompt, plus the manifest and a canned task inline (no tools
in CI, so the skill is injected rather than read). The validator then
checks the output deterministically.

This tests prompt robustness — that the dispositions and contract
survive contact with a model — not Claude Code's dispatch mechanics.

Env: GITHUB_TOKEN (required), WO_MODEL (optional, default an
open-weights model; see https://github.com/marketplace/models).
"""
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validate_warrant import validate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ENDPOINT = "https://models.github.ai/inference/chat/completions"
MODEL = os.environ.get("WO_MODEL", "meta/Llama-3.3-70B-Instruct")
# Free-tier models occasionally truncate or drift even at low
# temperature; one conformant warrant out of ATTEMPTS passes, so a
# single bad sample doesn't fail CI while a broken prompt still does.
ATTEMPTS = int(os.environ.get("WO_ATTEMPTS", "3"))


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    system = strip_frontmatter(
        (ROOT / "agents" / "warrant-officer.md").read_text())
    manifest = (ROOT / "skills" / "claim-licensing" / "manifests" /
                "regression-empirical.md").read_text()
    task = (ROOT / "ci" / "smoke_task.md").read_text()

    user = (f"{task}\n\n--- MANIFEST (regression-empirical) ---\n"
            f"{manifest}")

    for attempt in range(1, ATTEMPTS + 1):
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

        output = data["choices"][0]["message"]["content"]
        print(f"--- model: {MODEL}, attempt {attempt}/{ATTEMPTS} ---\n"
              f"{output}\n--- end output ---\n")

        problems = validate(output, manifest="regression-empirical")
        if not problems:
            print("smoke test: model produced a conformant warrant")
            return
        print(f"attempt {attempt}: warrant non-conformant:")
        for p in problems:
            print(f"  - {p}")

    print(f"SMOKE TEST FAILED — no conformant warrant in "
          f"{ATTEMPTS} attempts")
    sys.exit(1)


if __name__ == "__main__":
    main()
