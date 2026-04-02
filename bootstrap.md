# Bootstrap

This is the initialization prompt for a new autonomous reverse-engineering project. Your goal is to create a clean, seperated workspace for a single target and prepare it for the runtime agent (`program.md`). Do not perform reverse engineering yet.

## Goal & Deliverables

Create a dedicated workspace at `projects/<project-slug>/` (slug based on target/date) containing:

- `program.md` (copied from root)
- `goal.md`
- `context.md`
- `progress.md`
- `attempts.md` & `attempts.tsv`
- `paths.md`
- `inbox/` (with `README.md`)
- `knowledge-base/` (with `index.md`, `facts.md`, `hypotheses.md`, `disproved.md`)
- Directories: `artifacts/` (source evidence), `derived/` (outputs), `scripts/` (tooling), `logs/`

## Bootstrap Workflow

1. **Ask Required Info** (if unknown): Target name, exact goal, target type (e.g., APK, BLE, firmware), available artifacts, live interaction capability, safety/legal boundaries, and stop/continue behavior on hard blocks.
2. **Suggest Optional Resources**: Propose 2-3 high-value, target-specific resources (e.g., clean BLE capture, decrypted APK, firmware dump) that would accelerate progress.
3. **Initialize Workspace**: Create the directory structure and populate the markdown files with practical starter content based on the gathered context. Do not invent missing artifacts.
4. **Handoff**: Output the workspace path, readiness state, critical missing resources, and exact instructions to launch the main run using `program.md`.

## File Initialization Rules

- **`goal.md`**: Target name, exact end goal, success criteria, constraints, non-goals.
- **`context.md`**: Target type, available artifacts, environment access, human capabilities, constraints, initial hypotheses.
- **`progress.md`**: Phase (bootstrap complete), baseline summary, known blockers, confidence level.
- **`attempts.md`**: Empty section or note.
- **`attempts.tsv`**: Header: `attempt_id\tstatus\tconfidence\tcategory\thypothesis\tsummary\tartifacts`
- **`paths.md`**: Investigation paths organized by status (ready / in-progress / blocked / completed) with inline blocker tracking and trigger conditions.
- **`inbox/README.md`**: Drop-zone instructions listing currently requested human-provided files and where to place them.

*Note: Prefer `partially blocked` over `blocked` if any useful work can begin.*
