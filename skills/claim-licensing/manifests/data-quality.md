# Manifest: data quality / pipeline claims

Covers: fitness-for-purpose of datasets, joinability of sources,
transformation faithfulness through pipelines, trustworthiness of
channels/sensors. Anything asserting that data can be relied on for a
stated use.

## Error profile

| Class          | Status   | Bounded by                              |
|----------------|----------|------------------------------------------|
| Completeness   | LIVE     | coverage % over the required window; gaps located and characterized (random vs. structured) |
| Accuracy/units | LIVE     | range checks against physical envelopes; unit-sniff at known discontinuities (maintenance, firmware, schema changes) |
| Consistency    | LIVE     | internal invariants close (see Verification); cross-source agreement on overlap windows |
| Identity/join  | LIVE when joining | match rate on the join key; unmatched records analyzed, not dropped silently |
| Temporal       | LIVE     | clock-skew and timezone/DST audit; alignment error bounded at the resolution the purpose needs |
| Lineage        | CRITICAL | every transformation stage named; row/mass conservation checked across each stage |

Declare the dominant class first. Classes irrelevant to the claim
(e.g. identity/join for a single-source claim) are declared absent,
not skipped.

## Envelope (pre-profiling, blocking)

1. **Fermi yardstick**: expected volume, ranges, and rates from first
   principles (a 1 Hz channel over a year is ~31.5M rows; speeds,
   powers, and flows have physical envelopes). Write the expectation
   before profiling. Found values violating it are wrong until shown
   otherwise.
2. **Purpose fit**: state what question this data must answer, at
   what resolution and coverage. The claim is licensed against this
   purpose, not against data quality in the abstract.

## Verification

Physical invariants where they exist (integrated speed vs. distance,
energy/mass balances, flow vs. power relationships) — an invariant
either closes or it doesn't, making this the least fakeable gate.
Where no physics applies: row-count and checksum conservation across
every transformation stage.

## Falsification menu (spend at least 2)

- Stratified sample-and-eyeball: inspect raw records across strata;
  never trust aggregates alone.
- Cross-source reconciliation on an overlap window with an
  independent source.
- Duplicate probe: exact and near-duplicate detection on the claimed
  key.
- Boundary probe: year ends, DST transitions, schema-change dates,
  operational edges (e.g. port calls) — where pipelines break.
- Null-pattern analysis: are gaps random or structured (by time,
  entity, or channel)?
- Unit-sniff: magnitude discontinuities at known maintenance or
  configuration dates.

## Honest-exit template for the warrant's ERROR field

"Completeness: X% coverage over <window>, gaps <located and
characterized>. Accuracy: ranges within physical envelope except
<exceptions>. Consistency: <invariants> close within <Z>. Join: Y%
match on <key>, unmatched <analyzed>. Temporal: aligned to <resolution>.
Lineage: <n> stages, conservation checked at each. Dominant risk:
<class>, bounded by <check>. Fit for <stated purpose>; NOT licensed
for <adjacent uses this was not validated against>."

Note the final clause is mandatory for this family: the
characteristic data failure is reuse outside the validated purpose.
A data warrant should travel with its dataset as a datasheet with
teeth.
