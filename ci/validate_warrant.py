#!/usr/bin/env python3
"""Validate that text contains a conformant warrant.

This is the deterministic grader for the CI smoke cases (and usable
locally: `python ci/validate_warrant.py <manifest-id> < warrant.md`).
It checks shape and the machine-checkable honesty obligations, not
truth: required fields, a legal STATUS, per-family hard rules (absent
error classes declared rather than faked; the data family's mandatory
NOT-licensed-for clause), and any per-case expectations from an
expect.json (required STATUS values, required/forbidden patterns).
"""
import json
import re
import sys

REQUIRED = ["CLAIM:", "FOR:", "METHOD:", "ENVELOPE:", "LOAD-BEARING:",
            "ERROR:", "FALSIFICATION:", "STATUS:", "RECONSTRUCT:"]


def _error_block(text: str) -> str:
    if "ERROR:" not in text:
        return ""
    return text[text.find("ERROR:"):text.find("FALSIFICATION:")]


def _check_regression_empirical(text: str, problems: list) -> None:
    error_block = _error_block(text)
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


def _check_data_quality(text: str, problems: list) -> None:
    if not re.search(r"NOT licensed", text, re.IGNORECASE):
        problems.append(
            "data-family warrant missing the mandatory "
            "'NOT licensed for' clause")


FAMILY_CHECKS = {
    "regression-empirical": _check_regression_empirical,
    "data-quality": _check_data_quality,
}


def validate(text: str, manifest: str = "", expect: dict = None) -> list[str]:
    problems = []

    for field in REQUIRED:
        if field not in text:
            problems.append(f"missing field {field}")

    m = re.search(r"STATUS:\s*(CLOSED|DEAD-END)", text)
    if not m:
        problems.append("STATUS must be CLOSED or DEAD-END")

    if manifest in FAMILY_CHECKS:
        FAMILY_CHECKS[manifest](text, problems)

    if expect:
        allowed = expect.get("status_in")
        if allowed and m and m.group(1) not in allowed:
            problems.append(
                f"STATUS is {m.group(1)}, expected one of {allowed} "
                "for this case")
        for pattern, why in expect.get("require_regex", []):
            if not re.search(pattern, text, re.IGNORECASE):
                problems.append(f"missing expected content: {why}")
        for pattern, why in expect.get("forbid_regex", []):
            if re.search(pattern, text, re.IGNORECASE):
                problems.append(f"forbidden content present: {why}")

    return problems


def claim_number(text: str) -> float | None:
    """First numeric value after CLAIM:, for informational checks."""
    m = re.search(r"CLAIM:.*?(-?\d[\d,]*(?:\.\d+)?)", text, re.DOTALL)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def main() -> None:
    text = sys.stdin.read()
    manifest = ""
    expect = None
    args = sys.argv[1:]
    if args and args[0] == "--expect":
        expect = json.loads(open(args[1]).read())
        manifest = expect.get("manifest", "")
    elif args:
        manifest = args[0]
    problems = validate(text, manifest, expect)
    if problems:
        print("WARRANT NON-CONFORMANT:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print("warrant: conformant")


if __name__ == "__main__":
    main()
