# auto-reverse-engineer

`auto-reverse-engineer` is a prompt framework for running autonomous reverse-engineering projects in an existing coding-agent harness.

## Files

- `bootstrap.md`: creates a new project workspace, asks for the required context, and prepares the run
- `program.md`: runs the actual reverse-engineering loop inside that project workspace
- `tactics.md`: RE domain knowledge reference — target-type playbooks, analysis escalation ladder, pattern library, and anti-patterns

## How it works

1. Run an agent with `bootstrap.md`.
2. It creates a separate project folder for the target.
3. It writes the initial files such as `goal.md`, `project-context.md`, `progress.md`, `attempts.md`, `paths.md`, `inbox/`, and `knowledge-base/`.
4. It copies `program.md` and `tactics.md` into that project folder.
5. Start a second agent in the new project folder with `program.md`.

## Running it

From the repo root, first run `bootstrap.md` to create the project workspace.
In this example we use Codex, but the same can be done with Claude or any other agent harness.

```bash
codex "run bootstrap.md"
```

It will ask you for needed information and create the project workspace.

After bootstrap, start the main run from inside the created project folder:
For Codex, the agent does not always keep looping by itself, so run it in a shell loop from inside the project folder:

```bash
while true; do
    codex exec --yolo "run program.md, target projects/<project-slug>/goal.md" 2>&1 | tee -a agent.log
    sleep 1
done
```

Claude usually does not need a shell loop, so you can just run it once:

```bash
claude -p "run program.md"
```

## Project model

Each target gets its own workspace. The framework repo stays generic. The project folder holds the target-specific state, artifacts, notes, scripts, and logs.

The runtime agent should:

- work toward the goal in `goal.md`
- keep a structured knowledge base
- track attempts and avoid repeating failed work
- maintain `paths.md` with prioritized investigation paths, blockers, and trigger conditions
- poll `inbox/` each loop to detect when the human provides requested resources
- automatically unblock and pursue paths when trigger conditions are met
- always work on the highest-priority ready path
- consult `tactics.md` when seeding paths or choosing between approaches

## Example

A project could target a CGM app and sensor:

- inspect the APK
- recover the BLE protocol
- identify pairing and message parsing
- reach raw glucose data from the device

## Purpose

The point of this repo is simple: make autonomous reverse-engineering runs repeatable, structured, and isolated per target.
