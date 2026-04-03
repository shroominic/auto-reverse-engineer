# Auto Reverse Engineer — Claude Code Instructions

You are operating inside an autonomous reverse-engineering framework. Your workspace is a self-contained project folder with structured state files that you must read, respect, and maintain.

## Workspace Layout

```
projects/<slug>/
├── goal.md              # Success criteria — your north star
├── context.md           # Target info, constraints, environment
├── progress.md          # Current phase, blockers, confidence
├── attempts.md          # Narrative log of every experiment
├── attempts.tsv         # Structured attempt records (tab-separated)
├── paths.md             # Investigation paths ranked by priority
├── verify.md            # Verification protocol (run between iterations)
├── program.md           # The execution loop (your main instructions)
├── inbox/               # Human-provided resources — poll every loop
├── knowledge-base/      # Structured findings
│   ├── index.md         # Topic index
│   ├── facts.md         # Confirmed findings with evidence
│   ├── hypotheses.md    # Unconfirmed but plausible
│   └── disproved.md     # Ruled out (with reason)
├── artifacts/           # Original target files — NEVER modify
├── derived/             # Your analysis outputs
├── scripts/             # Helper tools you create
└── logs/                # Detailed execution logs
```

## Core Rules

1. **Read before acting.** On every loop iteration, re-read `goal.md`, `progress.md`, `paths.md`, and `inbox/` before choosing your next experiment.
2. **Never fabricate certainty.** If confidence is low, say so. Record it in `attempts.tsv`.
3. **Never modify `artifacts/`.** These are source evidence. Copy to `derived/` for analysis.
4. **Record everything.** Every experiment gets an entry in both `attempts.md` and `attempts.tsv`, even failures.
5. **One hypothesis per experiment.** Don't test multiple things at once — isolate variables.
6. **Cheapest test first.** Before running a complex analysis, check if a simpler method answers the same question.

## Using Your Capabilities

### Subagents for Parallel Paths

When `paths.md` has multiple ready paths, spawn subagents to investigate in parallel:

```
- Path A (ready, high priority): static analysis of binary → assign to subagent
- Path B (ready, medium priority): network traffic analysis → assign to subagent
- Path C (blocked on human): needs firmware dump → skip, queue in inbox/
```

Each subagent should:
- Work on exactly one path
- Write findings to `knowledge-base/` and `derived/`
- Log its attempt in `attempts.md` / `attempts.tsv`
- Update `paths.md` with results

### Tool Use

Use your native tools aggressively:
- **Bash**: Run `strings`, `xxd`, `file`, `binwalk`, `objdump`, `readelf`, `nm`, `radare2`, `frida`, `adb`, and any other RE tool available in the environment
- **Read/Write**: Maintain workspace files, parse binary data, manage the knowledge base
- **Grep/Glob**: Search across artifacts and derived outputs for patterns, strings, signatures
- **Web**: Look up file format specs, protocol documentation, CVE databases, vendor references

### Structured Thinking

Before each experiment:
1. State the hypothesis clearly
2. Define what evidence would confirm or disprove it
3. Choose the simplest method that produces that evidence
4. Set a time box (default: 15-30 minutes)

After each experiment:
1. Record the outcome honestly
2. Update `knowledge-base/` — move hypotheses to facts or disproved
3. Re-rank paths in `paths.md` based on new information
4. Check if any blocked path is now unblocked

## Verification

Run `verify.md` periodically (every 3-5 experiments, or when you think you've hit a milestone). It validates:
- Knowledge base consistency (no contradictions between facts)
- Progress claims backed by evidence
- Attempt log completeness
- Path rankings reflect current knowledge

## When You're Stuck

1. Re-read `knowledge-base/facts.md` — compound what you know
2. Check `attempts.md` for patterns in failures
3. Attack from a different layer (static → dynamic → network → crypto)
4. Create a helper script in `scripts/` to automate repetitive analysis
5. Queue specific, actionable requests in `inbox/README.md` for the human
6. **Never stop.** A blocked path is not a blocked run — switch paths and keep moving.
