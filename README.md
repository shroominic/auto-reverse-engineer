# auto-reverse-engineer

`auto-reverse-engineer` is a prompt framework for running autonomous reverse-engineering projects in an existing coding-agent harness.

## Files

- `bootstrap.md`: creates a new project workspace, asks for the required context, and prepares the run
- `program.md`: runs the actual reverse-engineering loop inside that project workspace

## How it works

1. Run an agent with `bootstrap.md`.
2. It creates a separate project folder for the target.
3. It writes the initial files such as `goal.md`, `context.md`, `progress.md`, `attempts.md`, `paths.md`, `inbox/`, and `wiki/`.
4. It copies `program.md` into that project folder.
5. It spawns the runtime agent in a new tmux session automatically.

## Running it

From the repo root:

```bash
claude "run bootstrap.md"
```

Bootstrap asks for the target details, creates the workspace, and starts the runtime in a tmux session. Attach with `tmux attach -t <project-slug>`. Use whatever harness you like.

## Project model

Each target gets its own workspace. The framework repo stays generic. The project folder holds the target-specific state, artifacts, notes, scripts, and logs.

The runtime agent should:

- work toward the goal in `goal.md`
- build and maintain its own wiki at `wiki/` (interlinked markdown pages, compounding knowledge)
- track attempts and avoid repeating failed work
- maintain `paths.md` with prioritized investigation paths, blockers, and trigger conditions
- poll `inbox/` each loop to detect when the human provides requested resources
- automatically unblock and pursue paths when trigger conditions are met
- always work on the highest-priority ready path

## Example

A project could target a CGM app and sensor:

- inspect the APK
- recover the BLE protocol
- identify pairing and message parsing
- reach raw glucose data from the device

## Purpose

The point of this repo is simple: make autonomous reverse-engineering runs repeatable, structured, and isolated per target.
