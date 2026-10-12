---
name: auto-reverse-engineer
description: Run persistent reverse-engineering investigations from binaries, app packages, captures, or devices, producing a tested reconstruction or decoder with cited evidence.
---

# Auto Reverse Engineer

Investigate one target in your existing agent harness. Keep the workspace as
durable memory and finish with an executable acceptance check.

## Start

Resolve the target, exact goal, available artifacts/access, constraints, and a
checkable deliverable. Reuse known context; ask only for missing essentials.
For protocol work, prefer a decoder tested against held-out frames or declared
exchanges. Agree on the evidence and cases that count as success.

Resolve `scripts/are.py` relative to this skill's folder and initialize with
`init PATH --goal "..." --verify "COMMAND"`.
It copies this skill and the helper into the workspace. Put original inputs in
`artifacts/`; record target identity, scope, and non-goals in `goal.md`.
Use the existing harness directly or the helper's bounded `run` command.

Inside the project:

- `goal.md`: goal, target, context, constraints.
- `plan.json`: prioritized paths; `ready`, `blocked`, or `done`.
  Each has `id`, positive `priority` (1 is highest), `question`, and
  `blocked_on` (inbox filenames). `action` is `continue` or `verify`.
- `attempts.jsonl` and `evidence/`: one attempt log with hashed snapshots.
- `wiki.md`: facts, hypotheses, disproved ideas, unresolved questions.
- `inbox/REQUESTS.md`: resource requests and the questions they unblock.
- `derived/`, `scripts/`, `logs/`: outputs, tooling, execution records.
- `run.json`: helper-owned state, budgets, input hashes, acceptance receipt.

## Investigate

Read the goal, plan, latest attempts, and relevant findings on each pass.
Inspect new inputs before trusting them. Select the highest-priority ready path;
a blocked branch does not block useful work elsewhere.

State a falsifiable hypothesis and run the cheapest useful, bounded experiment.
Retry a failure with new evidence or a fixed blocker. Write small probes or
decoders when they answer the question faster. Independent workers may collect
evidence; one owner updates the plan and wiki.

Save raw output, then record the attempt:

```sh
python3 are.py record . --hypothesis "..." --method "..." --outcome "..." \
  --kind observed --evidence logs/probe.txt --limitations "..."
```

Use `observed` for direct measurements, `derived` for computations, and
`inferred` for interpretations. Cite attempt IDs and snapshot paths in the wiki.
Keep partial results, failures, contradictions, and search boundaries.
Update only affected findings; reread source evidence for consequential uncertain
claims. Mark superseded hypotheses disproved and re-rank paths.

Preserve original inputs and recorded snapshots. The helper rejects changed or
missing pinned inputs and evidence. Keep new capture versions under new names.
To block a path, name the missing resource in `blocked_on` and REQUESTS.md.
A resumed runner makes it ready when those files arrive; validate their contents.
Do not edit helper state or budgets to bypass a stop.

## Tools and completion

Use available tools directly. REA is an optional analysis backend: use its
installed skill, actual schemas, evidence, and provider limitations.
Static inspection does not establish execution; decompiled code is not original
source. Preserve artifact/provider identity; distinguish unsupported from absent.

Save/export complete REA evidence into the project before closing its session.
Link tool Evidence IDs to saved records; an ID alone is not durable evidence.
Use focused views of retained results before repeating expensive analysis.
Preserve harness permissions and the user's target/action scope.

Set `plan.json` action to `verify` when the declared checker is ready, or run
`python3 are.py verify .` directly. Evidence integrity and checker exit 0 are
required for completion. Check original/reference behavior with positive,
negative, malformed, and boundary cases appropriate to the claim.
Report the tested scope and remaining unknowns; finite cases do not prove
whole-program equivalence. Never weaken the checker to obtain a pass.

Stop on verified completion, interruption, execution failure, or budget exhaustion.
When no path is ready, request resources and wait. Do not invent busywork or
start another runner; the human can supply files and resume with the same budget.
