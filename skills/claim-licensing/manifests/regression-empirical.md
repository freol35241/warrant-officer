# Manifest: regression / empirical methods

Covers: statistical series methods (Holtrop-Mennen class), regression
formulae, Gaussian-process / Bayesian performance fits, ML
surrogates. Anything whose authority comes from data it was fitted
to, not from first principles.

## Error profile

| Class            | Status   | Bounded by                              |
|------------------|----------|-----------------------------------------|
| Iterative        | usually absent (present only if the fit itself uses an optimizer — then report optimizer convergence) | — |
| Discretization   | ABSENT — declare "no discretization concept applies" | — |
| Truncation       | ABSENT   | —                                        |
| Model-form       | DOMINANT | validity regime of the fitted form; known biases of the method for this vessel/system type |
| Statistical      | LIVE     | cross-validation error, posterior width, or the method's published scatter — quote a number |
| Input            | CRITICAL | applicability check (below) + sensitivity of output to input uncertainty |

## Envelope (pre-solve, blocking)

1. **Applicability**: verify every input parameter lies inside the
   ranges the method was fitted on (for Holtrop: Cb, L/B, B/T, Fr,
   etc.; for a custom fit: the training distribution). Record
   in-range / out-of-range per parameter.
2. **Yardstick**: independent order-of-magnitude estimate (reference
   vessel scaling, physics-based rough-out). Write the expected range
   before running the method.

## Verification / validation note

Verification in the CFD sense COLLAPSES for this class: the method is
its own fit. Do not manufacture a convergence study. The obligations
are applicability (above) + honest uncertainty (statistical class) +
regime statement (model-form class).

## Falsification menu (spend at least 2)

- Cross-check against independent data: operational/measured data,
  a sister vessel, a published installation, or a second independent
  method.
- Limiting behavior: does the output trend correctly as the dominant
  input goes to its physical limit?
- Perturbation: vary the most uncertain input across its plausible
  range; does the conclusion survive?
- Extrapolation probe: if any parameter was near the envelope edge,
  check output sensitivity to crossing it.

## Honest-exit template for the warrant's ERROR field

"Model-form dominant: method valid for <regime>, this case is
<inside/near-edge/outside>. Statistical: ±<X>% from <CV / posterior /
published scatter>. No discretization concept applies. Input:
<applicability result>; output sensitivity to dominant input
uncertainty: <Y>."
