# CLAUDE.md

Behavioral guidelines. Bias toward caution over speed; for trivial
tasks, use judgment.

## 0. Price the job first

Before any work: establish what the result is for and what rigour
that warrants. Scale everything below to that.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Match existing style, even if you'd do it differently.
- Remove imports/variables/functions that YOUR changes made unused;
  don't remove pre-existing dead code unless asked.

The test: every changed line traces directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

- "Fix the bug" → "Write a test that reproduces it, make it pass"
- For multi-step tasks, state a brief plan with a verify step per item.

## 5. Load-bearing claims go to the warrant officer

Any task producing a load-bearing result a decision relies on (a
number, a dataset judgment, an estimate) MUST be
dispatched to the `warrant-officer` subagent. Every dispatch states:
the task, the purpose (what decision it feeds), and the bar (required
precision, derived from the purpose). Accept only a conformant
warrant.md; a DEAD-END status is an acceptable, complete outcome.
Never pull workings from `runs/` into the main context; use the
RECONSTRUCT pointer only if the warrant is challenged.

## Lab diary

A running lab diary is maintained at `diary/`, one markdown file per
day. Update it when a design decision is made or deferred, an
experiment is run, a new idea is introduced, or something surprising
is observed. Reference warrants by path rather than restating
results. Brief, dated entries; a thinking tool, not a polished
document.
