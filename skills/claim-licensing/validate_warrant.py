#!/usr/bin/env python3
"""Deterministic warrant checker. Ships with the claim-licensing
skill so the warrant-officer can check its own warrant before
returning it (final coherence check), the dispatcher can check what
crosses the boundary, and CI can grade smoke cases.

Usage: python3 validate_warrant.py <manifest-id> < warrant.md
       python3 validate_warrant.py --expect <expect.json> < warrant.md

It checks shape and coherence, not truth: required fields, a legal
STATUS, per-family hard rules (absent error classes declared rather
than faked; the data family's mandatory NOT-licensed-for clause), and
the self-incrimination rule — a warrant whose own ENVELOPE/ERROR
records an out-of-envelope condition cannot be STATUS: CLOSED.
"""
import json
import re
import sys

REQUIRED = ["CLAIM:", "FOR:", "METHOD:", "ENVELOPE:", "LOAD-BEARING:",
            "ERROR:", "FALSIFICATION:", "STATUS:", "RECONSTRUCT:"]

# Negation-aware scanning: only affirmative statements count, so
# "inputs are inside the fitted range" or "extrapolation not
# required" never trigger.
_NEG = re.compile(r"\b(no|not|none|absent|n/?a|without|does not|"
                  r"doesn'?t|cannot|can'?t|inside|within|passed)\b",
                  re.IGNORECASE)


def _affirms(pattern: re.Pattern, block: str) -> bool:
    return any(pattern.search(seg) and not _NEG.search(seg)
               for seg in re.split(r"[.;\n]", block))


def _field_block(text: str, field: str, next_field: str) -> str:
    if field not in text:
        return ""
    start = text.find(field)
    end = text.find(next_field) if next_field in text else len(text)
    return text[start:end]


def _check_self_incrimination(text: str, problems: list) -> None:
    """CLOSED + a recorded out-of-envelope condition = the evidence
    contradicts the verdict. Every dishonest warrant observed in
    testing disclosed the convicting fact; this rule convicts it."""
    if not re.search(r"STATUS:\s*CLOSED", text):
        return
    out_of_envelope = re.compile(
        r"(outside (the )?(fitted|valid|applicabilit|training)|"
        r"out[ -]of[ -](range|envelope)|extrapolat|beyond the fitted)",
        re.IGNORECASE)
    for field, nxt in (("ENVELOPE:", "LOAD-BEARING:"),
                       ("ERROR:", "FALSIFICATION:")):
        if _affirms(out_of_envelope, _field_block(text, field, nxt)):
            problems.append(
                f"self-incriminating warrant: STATUS is CLOSED but "
                f"{field[:-1]} records an out-of-envelope/"
                "extrapolation condition — evidence contradicts "
                "verdict; an out-of-envelope result cannot be CLOSED "
                "against a quantitative bar")
            return


def _check_regression_empirical(text: str, problems: list) -> None:
    error_block = _field_block(text, "ERROR:", "FALSIFICATION:")
    mentions_absent_discretization = bool(re.search(
        r"(no\s+discretization|discretization[^.\n]*"
        r"(absent|not appl|n/?a\b|does not apply|none))",
        error_block, re.IGNORECASE))
    # "no convergence order applies" is the honest declaration the
    # skill mandates; only affirmative mentions count as fabricated.
    fab = re.compile(r"(observed order|convergence order|grid stud)",
                     re.IGNORECASE)
    if _affirms(fab, error_block):
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

    _check_self_incrimination(text, problems)

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
