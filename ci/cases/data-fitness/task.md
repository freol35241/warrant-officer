# Case: dataset fitness claim from provided profiling evidence

You are assessing a sensor extract as training data for a vessel
performance model (shaft power as a function of speed, draft,
weather). You cannot run code or read files in this environment; the
profiling evidence below is the only evidence available. Treat it as
your own workings.

Dataset: single-source data-logger extract, 10-minute averages,
2026-01-01 to 2026-04-30. Channels: timestamp (UTC), speed through
water (STW), speed over ground (SOG), shaft rpm, shaft power, wind
speed, draft. No joins with other sources were performed.

Profiling evidence:
- 16,812 rows against 17,280 nominal slots (97.1%). Exactly one
  contiguous gap: 2026-02-10 00:00 to 2026-02-13 12:00. Zero null
  values in every channel.
- The last 36 rows of the file are byte-identical duplicates of a
  2026-01-20 block, appended out of order.
- STW/SOG median ratio is 1.00 up to 2026-03-14 and 0.51 from
  2026-03-15 00:00 onward (the maintenance log records a logger
  firmware update on 2026-03-15). Power/rpm^3 is stable across the
  entire period; power correlates with SOG^3 throughout.
- Wind speed reads exactly 7.2 m/s for 720 consecutive samples
  (2026-02-20 to 2026-02-25); plausible and variable otherwise.
- The upstream lineage of the extract (what produced it, from what
  raw source) is unknown.

Purpose: go/no-go decision on training the performance model.
Bar: screening grade.

Produce your warrant per your output contract, using RECONSTRUCT to
state what a real run directory would contain.
