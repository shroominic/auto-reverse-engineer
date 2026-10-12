# auto-reverse-engineer

Persistent reverse engineering in your existing agent harness. Recover a tested
decoder or reconstruction, keeping evidence and unfinished paths between runs.

One skill and one Python helper. No Python dependencies. Python 3.11+ on Linux/macOS.

## Start

Clone this repo, then ask your agent to use [SKILL.md](SKILL.md). You can also install it:

```sh
npx skills add shroominic/auto-reverse-engineer --skill auto-reverse-engineer
```

Create a workspace with an explicit acceptance command:

```sh
python3 scripts/are.py init projects/sensor \
  --goal "Recover the message format and build a decoder that passes saved frame tests" \
  --verify "python3 scripts/check.py" --max-turns 20 --timeout 900
```

Put inputs in `projects/sensor/artifacts/`, fill in context and constraints in
`goal.md`, and work in that folder with your agent. Build `scripts/check.py`
against original/reference behavior; an explanation alone is not completion.

For bounded unattended passes:

```sh
python3 projects/sensor/are.py run projects/sensor -- claude -p
```

The helper appends the skill/task prompt as the last argument to your chosen
noninteractive agent command. It uses your harness's existing permissions.
Each agent/check invocation has a deadline; turns persist across restarts.
Logs and the result live in the workspace. Completion requires saved evidence
and a passing checker. Failed checks return to investigation.

If all paths are blocked, it stops in `waiting`. Supply requested inbox files
and run the same command again. Verified completion never restarts the agent.
`exhausted` exits 2; execution/integrity errors exit 1; interruption exits 130.
Waiting and completion exit 0; read `run.json` to distinguish them.

To check a project directly:

```sh
python3 projects/sensor/are.py verify projects/sensor
```

REA is optional. Use [REA's setup instructions](https://github.com/morluto/rea)
and its matching skill/tools. Save evidence bundles before closing a session.
This framework borrows its evidence discipline, explicit limits, and verified
completion; it does not bundle analysis engines.

The helper pins inputs and snapshots attempt evidence. Workspaces are directories,
not security sandboxes; commands use your user permissions. It cleans child process
groups, not deliberately detached processes. Existing prompt-only projects need
a new workspace; copy inputs and carry forward findings after checking citations.

```sh
python3 -m unittest discover -s tests -v
```

MIT. See [LICENSE](LICENSE).
