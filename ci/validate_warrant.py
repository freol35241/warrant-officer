#!/usr/bin/env python3
"""Validate that text contains a conformant warrant.

This is the deterministic grader for the CI smoke test (and usable
locally: `python ci/validate_warrant.py < warrant.md`). It checks
shape, not truth: required fields, a legal STATUS, and — for the
regression-empirical manifest — that absent error classes are
declared rather than faked.
"""
import re
import sys

REQUIRED = ["CLAIM:", "FOR:", "METHOD:", "ENVELOPE:", "LOAD-BEARING:",
            "ERROR:", "FALSIFICATION:", "STATUS:", "RECONSTRUCT:"]


def validate(text: str, manifest: str = "") -> list[str]:
    problems = []

    for field in REQUIRED:
        if field not in text:
            problems.append(f"missing field {field}")

    if not re.search(r"STATUS:\s*(CLOSED|DEAD-END)", text):
        problems.append("STATUS must be CLOSED or DEAD-END")

    if manifest == "regression-empirical":
        # Absent classes must be declared, and a convergence order
        # must NOT be fabricated for a method that has none.
        error_block = text[text.find("ERROR:"):text.find(
            "FALSIFICATION:")] if "ERROR:" in text else ""
        mentions_absent_discretization = bool(re.search(
            r"(no\s+discretization|discretization[^.\n]*"
            r"(absent|not appl|n/?a\b|does not apply|none))",
            error_block, re.IGNORECASE))
        # "no convergence order applies" is the honest declaration the
        # skill mandates; only affirmative mentions count as fabricated.
        fab = re.compile(r"(observed order|convergence order|grid stud)",
                         re.IGNORECASE)
        neg = re.compile(r"\b(no|not|none|absent|n/?a|without|does not|"
                         r"doesn'?t|cannot|can'?t)\b", re.IGNORECASE)
        fabricates_order = any(
            fab.search(seg) and not neg.search(seg)
            for seg in re.split(r"[.;\n]", error_block))
        if fabricates_order:
            problems.append(
                "ERROR field claims convergence evidence for a "
                "regression method — fabricated warrant")
        elif not mentions_absent_discretization:
            problems.append(
                "ERROR field must declare discretization absent "
                "for regression-empirical methods")
        if not re.search(r"(model.form|statistical)", error_block,
                         re.IGNORECASE):
            problems.append(
                "ERROR field must address model-form and/or "
                "statistical error for this manifest")

    return problems


def main() -> None:
    text = sys.stdin.read()
    manifest = sys.argv[1] if len(sys.argv) > 1 else ""
    problems = validate(text, manifest)
    if problems:
        print("WARRANT NON-CONFORMANT:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("warrant: conformant")


if __name__ == "__main__":
    main()
