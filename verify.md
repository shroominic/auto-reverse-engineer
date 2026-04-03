# Verify

This is the verification prompt for an autonomous reverse-engineering project. Run this between experiment iterations to validate progress, catch inconsistencies, and ensure rigor. This is a checkpoint, not busywork — be honest and concise.

## When to Run

- Every 3-5 experiments
- After claiming a milestone or phase completion
- When confidence in `progress.md` jumps significantly
- Before requesting human resources (ensure the request is justified)

## Verification Checklist

### 1. Knowledge Base Consistency

- Read `knowledge-base/facts.md`, `hypotheses.md`, and `disproved.md`.
- Check: Are any facts contradicted by other facts?
- Check: Are any current hypotheses already disproved?
- Check: Are there hypotheses that should be promoted to facts (sufficient evidence) or demoted to disproved?
- Fix any inconsistencies found. Log corrections in `attempts.md` as a verify step.

### 2. Progress Integrity

- Read `progress.md` and compare claims against `knowledge-base/facts.md`.
- Every progress claim must reference specific evidence (file paths, tool output, artifact hashes).
- If a claim lacks evidence, downgrade confidence or re-run the experiment.
- Update `progress.md` with corrected confidence levels.

### 3. Attempt Log Completeness

- Compare `attempts.md` entries against `attempts.tsv`.
- Every experiment must appear in both.
- Check for missing fields: status, confidence, hypothesis, artifacts.
- Fill in any gaps.

### 4. Path Ranking Audit

- Read `paths.md` and cross-reference with latest `knowledge-base/`.
- Are blocked paths correctly blocked? Has new evidence unblocked anything?
- Are path priorities still correct given current knowledge?
- Are there superseded paths that should be marked completed or abandoned?
- Remove or deprioritize paths that are no longer relevant.

### 5. Artifact Integrity

- Verify `artifacts/` directory is unmodified (no accidental writes).
- Check that `derived/` outputs reference their source artifacts.
- Ensure `scripts/` tools are documented (what they do, how to run them).

### 6. Goal Distance

- Re-read `goal.md`.
- Estimate remaining distance to each success criterion.
- Identify the critical path — what single experiment would most reduce remaining uncertainty?
- Record this assessment at the bottom of `progress.md`.

## Output

After verification, append a summary to `progress.md`:

```md
## Verification — [timestamp]
- Knowledge base: [clean | N inconsistencies fixed]
- Progress claims: [all evidenced | N claims downgraded]
- Attempt log: [complete | N gaps filled]
- Path ranking: [current | N paths re-ranked]
- Artifacts: [intact | issues noted]
- Goal distance: [estimate]
- Critical next experiment: [description]
```

Then return to `program.md` and continue the experiment loop.
