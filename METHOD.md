# Method Notes

## Scope

Local-first validation of agent run artifacts, hashed run reports, and a
synthetic deletion proof. The package is deliberately small and runs without
network access.

## Invariants

- run directories are read-only;
- a run is valid only when a non-empty `output/structured.json` (or
  `results/structured.json`) exists;
- missing or malformed artifacts produce explicit failure codes, never silent
  success;
- `report` is canonical and reproducible through `report_hash`;
- `deletion-proof` uses synthetic records only and is idempotent;
- no prompt, response, credential, or private run is included.

## Limitations

Agent quality, learner evidence, and model comparison are outside this package.
The deletion proof is a process check, not a compliance certification.
