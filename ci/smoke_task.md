# Smoke task (canned dispatch)

Estimate the calm-water resistance of a cargo vessel at 14 knots using
the following fitted regression (a Holtrop-class empirical method).

Fitted model (from a published series):
    R_total [kN] = 0.85 * V^2.1        (V in knots)
    Method fitted on: V in 8-16 kn, Cb 0.65-0.80, L/B 5.5-7.5
    Published scatter of the method: +/-9% (1 sigma)

This vessel: Cb = 0.72, L/B = 6.4, V = 14 kn.

Purpose: screening propulsion options for a feasibility memo.
Bar: +/-15% on resistance is sufficient. Screening grade, not
guarantee grade.

You cannot run code or read files in this environment. The manifest
for regression/empirical methods is provided below; produce your
warrant per your output contract, using RECONSTRUCT to state what a
real run directory would contain (name the formula, inputs, and this
task file as the reconstruction basis).
