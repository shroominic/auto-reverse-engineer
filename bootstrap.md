# bootstrap

This is the initialization prompt for a new autonomous reverse-engineering project.

Your job is not to do the reverse engineering yet. Your job is to create a clean, isolated project workspace for one target, gather the minimum required context, identify missing prerequisites, and prepare the workspace so a second agent can execute `program.md`.

## Goal

Create a dedicated project environment that does not depend on using the framework repo as the active working memory. The framework repo is only the source of reusable instructions and templates. The actual reverse-engineering work should happen inside a separate project subfolder.

By the end of bootstrap, there should be a ready-to-run workspace with:

- a clear `goal.md`
- a filled `project-context.md`
- a copied `program.md`
- initialized tracking files
- a `setup-report.md` explaining readiness, gaps, and recommended next actions

## What you are creating

Create a new project workspace in a subfolder such as:

- `projects/<project-slug>/`

The exact slug should be based on the target and current date or another stable identifier.

The workspace should contain at least:

- `program.md`
- `goal.md`
- `project-context.md`
- `progress.md`
- `attempts.md`
- `attempts.tsv`
- `paths.md`
- `setup-report.md`
- `knowledge-base/index.md`
- `knowledge-base/facts.md`
- `knowledge-base/hypotheses.md`
- `knowledge-base/disproved.md`
- `artifacts/`
- `derived/`
- `scripts/`
- `logs/`
- `human-inputs/`
- `human-inputs/README.md`

## Bootstrap behavior

You must do all of the following:

1. Ask the user for the minimum required information.
2. Propose useful optional resources the user could provide up front.
3. Create the project workspace.
4. Copy the root `program.md` into the new project workspace as `program.md`.
5. Write the initial project files.
6. Tell the user exactly how to start the main run afterward.

Your bootstrap job ends when the project workspace is ready and the handoff instructions are written.

## Required questions

Ask for the following if they are not already known:

1. project name or target name
2. exact goal state
3. target type
4. artifacts already available
5. whether live interaction with the target is possible
6. safety or legal boundaries
7. whether the autonomous run should stop on hard block or always keep trying alternate paths

Examples of target type:

- Android APK
- iOS app
- BLE device
- firmware image
- desktop binary
- network protocol
- hardware accessory

## Optional resource suggestions

After learning the target type, propose a small list of high-value optional resources the user could provide.

Examples:

For BLE targets:

- the APK or app version involved
- the device physically nearby and powered on
- a clean BLE pairing or session capture
- Android logcat output
- nRF Connect exports
- permission to use Bluetooth tooling

For APK targets:

- the APK file
- split APKs if applicable
- prior APK versions for diffing
- known endpoint information
- decompiled output if already available

For firmware targets:

- firmware dump or update package
- hardware revision and model number
- boot logs
- UART, JTAG, or SWD access if available
- multiple firmware versions for diffing

Only suggest resources that are realistic and likely to unlock major progress.

## Workspace writing rules

When you create the workspace:

- keep source evidence in `artifacts/`
- keep derived outputs in `derived/`
- keep helper tooling in `scripts/`
- keep persistent memory in the markdown files and `knowledge-base/`
- keep logs in `logs/`

Do not pretend missing artifacts exist. If the user has not yet provided something, record it as missing in `setup-report.md` and, if useful, add a blocked path to `paths.md` with a trigger condition pointing to `human-inputs/`.

## File initialization rules

Write the files with practical starter content.

`goal.md` should contain:

- the target name
- the exact end goal
- concrete success criteria
- constraints and boundaries
- any known non-goals

`project-context.md` should contain:

- target type
- currently available artifacts
- environment access available to the agent
- human capabilities available on request
- known constraints
- initial hypotheses or likely attack surfaces

`progress.md` should contain:

- current phase set to bootstrap complete
- a short baseline summary
- known blockers
- current confidence level

`attempts.md` should start with an empty section or a note that no experiments have run yet.

`attempts.tsv` must start with this header:

```tsv
attempt_id	status	confidence	category	hypothesis	summary	artifacts
```

`paths.md` should contain the initial investigation paths the runtime agent should consider. Each path must follow the format defined in `program.md`. Specifically:

- Create a summary table at the top with sections for **Waiting on human**, **Ready now**, **Blocked**, and **Completed**.
- Add one path entry per identified approach, with status, priority, estimated value, blockers (with trigger conditions), and description.
- For any missing artifact or recommended human action, create a path with status `blocked` and a trigger condition pointing to a specific file in `human-inputs/`.
- Ensure at least one path has status `ready` so the agent can begin immediately.

`human-inputs/README.md` should contain:

- a short explanation that this folder is the drop zone for human-provided files
- a list of currently requested items (mirroring the "Waiting on human" section from `paths.md`)
- instructions: place the file here, then the agent will detect it on its next loop iteration

`setup-report.md` should contain:

- project path
- what the user provided
- what is missing
- whether the project is ready now, partially blocked, or blocked
- recommended first actions
- exact instructions for launching the main run with `program.md`

## Readiness categories

Use one of these:

- `ready`: enough inputs exist for meaningful autonomous work now
- `partially blocked`: autonomous work can begin, but some important resources are missing
- `blocked`: meaningful work cannot start yet because essential prerequisites are missing

Prefer `partially blocked` over `blocked` whenever any useful work can still begin.

## Main handoff

At the end of bootstrap, tell the user:

1. the path of the created project workspace
2. the current readiness state
3. the most important missing artifacts or optional resources
4. how to launch the main autonomous run in that workspace using `program.md`

The runtime agent should then operate only inside that project workspace.

## Example result

If the target is a CGM BLE reverse-engineering project, bootstrap might produce:

- `projects/cgm-apr1/program.md`
- `projects/cgm-apr1/goal.md`
- `projects/cgm-apr1/project-context.md`
- `projects/cgm-apr1/paths.md`
- `projects/cgm-apr1/setup-report.md`
- `projects/cgm-apr1/artifacts/app.apk`
- `projects/cgm-apr1/human-inputs/README.md`

with `paths.md` containing a `ready` path for decompiling the APK and mapping BLE UUIDs, and a `blocked` path for analyzing a BLE handshake capture with trigger `file-exists: human-inputs/handshake.pcap`.

## Never confuse bootstrap with runtime

Bootstrap creates the environment.

Bootstrap does not do the long-running experiment loop.

Bootstrap should leave the user with a ready project and a clear handoff into `program.md`.
