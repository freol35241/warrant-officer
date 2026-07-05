---
name: claim-licensing
description: >
  Defines what evidence licenses a load-bearing claim, per claim
  family and method class. Consult this skill whenever you are about
  to report a result that a decision depends on and you must
  characterize its reliability — numerical results from ANY
  computational method (CFD, panel/BEM, FEA, ODE/time-domain,
  spectral, regressions, statistical or ML fits), data quality and
  pipeline claims (fitness-for-purpose, joinability, transformation
  faithfulness), and other claim families as manifests are added.
  Also consult it when choosing between methods, since manifests
  state each method's applicability envelope. Do not report a
  load-bearing result without having read the manifest for its class.
---

# Claim licensing by family and method class

## How to use this skill

Identify your claim's family and method class, and read exactly one
manifest from `manifests/`. The manifest tells you which error
classes are live for this class, what the envelope (pre-work) check
is, what evidence bounds each live class, the falsification menu,
and the honest-exit template for your warrant's ERROR field.

## Error classes are declared per claim family

There is no universal error taxonomy; each claim family has its own
recurring failure anatomy, and its manifests declare which classes
are live and how each is bounded. Name the DOMINANT class first: a
precise bound on a minor class does not license a claim while the
dominant class is uncharacterized.

**Numerical family** (results of computation):

1. **Iterative/solver** — solver stopped short (residuals, tolerances)
2. **Discretization** — continuum approximated by finite mesh/panels/
   timestep (refinement studies, observed order)
3. **Truncation** — infinite expansion cut off (mode/term sensitivity)
4. **Model-form** — the governing equations approximate reality
   (validation inside the regime + explicit regime edges; often
   dominant, often the honest answer is a regime statement)
5. **Statistical/sampling** — finite data, posterior, or draws
   (cross-validation, posterior width, held-out error)
6. **Input/data** — BCs, geometry, environment, training inputs are
   themselves uncertain (sensitivity, propagation, applicability
   check: is this input inside the population the method was built
   from?)

**Data family** (claims about datasets and pipelines):

1. **Completeness** — gaps, coverage windows, silent dropouts
2. **Accuracy/units** — miscalibration, magnitude slips, encoding rot
3. **Consistency** — internal invariants and cross-source agreement
4. **Identity/join** — entity resolution, duplicates, match rates
5. **Temporal** — clock skew, timezone/DST seams, alignment
6. **Lineage** — is the transformation chain from source to artifact
   actually known and reproducible?

## Hard rules

- An error class the manifest marks ABSENT must be declared absent in
  the warrant ("no discretization concept applies"), not silently
  skipped and never faked (do not invent a convergence order for a
  method that has none).
- If the input sits outside the manifest's applicability envelope,
  say so. An out-of-envelope result may be reported only as
  extrapolation, explicitly flagged, and cannot be STATUS: CLOSED
  against a quantitative bar.
- If no manifest exists for your claim's class, that is itself a
  finding: state which error classes you judge live, bound them as
  best you can, flag the missing manifest in your warrant, and
  proceed.

## Manifest index

Numerical family:
- `manifests/regression-empirical.md` — series methods (Holtrop
  class), regression formulae, statistical/ML fits, any fitted model

Data family:
- `manifests/data-quality.md` — dataset fitness-for-purpose,
  joinability, pipeline transformation faithfulness

Add one page per method class as they are encountered; copy the
structure of an existing manifest. Only write a manifest where the
evidence it demands is expensive to fabricate and cheap to check.
