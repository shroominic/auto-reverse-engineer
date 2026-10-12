#!/usr/bin/env python3
"""A small, local investigation runner. Python 3.11+, Linux/macOS."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)


def digest(path):
    require(path.is_file() and not path.is_symlink(), f"Expected a regular file: {path}")
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def seal(row):
    content = {key: value for key, value in row.items() if key != "sha256"}
    return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()


def local(root, name):
    require(isinstance(name, str) and name, "Expected a project-relative file path")
    path = root / name
    require(not Path(name).is_absolute() and ".." not in Path(name).parts,
            f"Path must stay in the project: {name}")
    require(path.resolve().is_relative_to(root), f"Path leaves the project: {name}")
    return path


@contextmanager
def lock(root, name):
    with (root / name).open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(f"Another writer owns {name}; retry after it finishes") from None
        yield


def files(root, directories):
    result = {}
    for directory in directories:
        require((root / directory).is_dir() and not (root / directory).is_symlink(),
                f"Expected a project directory: {directory}")
        for path in sorted((root / directory).rglob("*")):
            require(not path.is_symlink(), f"Symlink is not evidence: {path}")
            if path.is_file() and path != root / "inbox/REQUESTS.md":
                result[str(path.relative_to(root))] = digest(path)
    return result


def state(root):
    value = read(root / "run.json")
    require(isinstance(value, dict) and type(value.get("version")) is int
            and value["version"] == 1, "Invalid run.json version")
    for key in ("turns", "max_turns", "timeout"):
        require(type(value.get(key)) is int and value[key] >= (0 if key == "turns" else 1),
                f"Invalid run.json {key}")
    require(isinstance(value.get("status"), str)
            and value["status"] in {"ready", "running", "waiting", "complete",
                                   "exhausted", "failed", "interrupted"}, "Invalid run status")
    require(isinstance(value.get("verify"), list) and value["verify"]
            and all(isinstance(arg, str) and arg for arg in value["verify"]),
            "verify must be a nonempty command argument list")
    require(isinstance(value.get("inputs"), dict), "Invalid input manifest")
    return value


def plan(root):
    value = read(root / "plan.json")
    require(isinstance(value, dict) and isinstance(value.get("action"), str)
            and value["action"] in {"continue", "verify"}
            and isinstance(value.get("paths"), list), "Invalid plan.json")
    ids = set()
    for item in value["paths"]:
        require(isinstance(item, dict) and isinstance(item.get("id"), str)
                and item["id"] and item["id"] not in ids, "Path IDs must be unique")
        ids.add(item["id"])
        require(type(item.get("priority")) is int and item["priority"] > 0,
                "Path priority must be a positive integer; 1 is highest")
        require(isinstance(item.get("status"), str)
                and item["status"] in {"ready", "blocked", "done"}
                and isinstance(item.get("question"), str) and item["question"].strip(),
                f"Invalid investigation path: {item['id']}")
        require(isinstance(item.get("blocked_on"), list), "blocked_on must be a list")
        for name in item["blocked_on"]:
            require(isinstance(name, str) and name.startswith("inbox/")
                    and name != "inbox/REQUESTS.md", "Triggers must name inbox evidence")
            local(root, name)
        if item["status"] == "blocked" and item["blocked_on"]:
            if all(local(root, name).is_file() for name in item["blocked_on"]):
                item["status"] = "ready"
    write(root / "plan.json", value)
    return value


def attempts(root):
    count = 0
    with (root / "attempts.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            require(isinstance(row, dict) and row.get("id") == f"ATTEMPT-{count + 1:04d}",
                    "Invalid attempt sequence")
            require(row.get("sha256") == seal(row), "Attempt record changed")
            require(isinstance(row.get("kind"), str)
                    and row["kind"] in {"observed", "derived", "inferred"}, "Invalid evidence kind")
            for key in ("hypothesis", "method", "outcome"):
                require(isinstance(row.get(key), str) and row[key].strip(), f"Missing attempt {key}")
            require(isinstance(row.get("evidence"), list) and row["evidence"],
                    "An attempt needs saved evidence")
            for item in row["evidence"]:
                require(isinstance(item, dict) and isinstance(item.get("sha256"), str),
                        "Invalid evidence reference")
                path = local(root, item.get("snapshot"))
                require(path.is_relative_to(root / "evidence"), "Snapshot must be in evidence/")
                require(digest(path) == item["sha256"], f"Evidence changed: {item['snapshot']}")
            count += 1
    return count


def inspect(root, value):
    current = files(root, ("artifacts", "inbox"))
    for name, sha in value["inputs"].items():
        require(current.get(name) == sha, f"Input changed or disappeared: {name}")
    changed = current != value["inputs"]
    value["inputs"] = current
    attempts(root)
    return changed


def invoke(root, command, log, timeout):
    with log.open("wb") as output:
        process = subprocess.Popen(command, cwd=root, stdin=subprocess.DEVNULL,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            raise ValueError(f"Deadline of {timeout}s reached; see {log.relative_to(root)}") from None
        finally:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def verify(root, value):
    inspect(root, value)
    require(attempts(root), "Record evidence before requesting completion")
    goal_hash = digest(root / "goal.md")
    descriptor, name = tempfile.mkstemp(prefix="verify-", suffix=".log", dir=root / "logs")
    os.close(descriptor)
    log = Path(name)
    code = invoke(root, value["verify"], log, value["timeout"])
    inspect(root, value)
    require(digest(root / "goal.md") == goal_hash, "Goal changed during acceptance")
    value["reason"] = f"Acceptance check exit {code}; see {log.relative_to(root)}"
    if code == 0:
        value["status"] = "complete"
        value["verification"] = {
            "command": value["verify"], "exit_code": code,
            "goal_sha256": goal_hash,
            "log": str(log.relative_to(root)), "sha256": digest(log),
            "outputs": files(root, ("derived", "scripts")),
        }
    else:
        value["status"] = "ready"
        value.pop("verification", None)
    write(root / "run.json", value)
    return code


def init(args, root):
    require(args.goal.strip(), "A goal is required")
    command = shlex.split(args.verify)
    require(command, "An executable acceptance check is required")
    require(args.max_turns > 0 and args.timeout > 0, "Budgets must be positive")
    source = Path(__file__).resolve()
    skill = source.parent.parent / "SKILL.md" if source.parent.name == "scripts" else source.parent / "SKILL.md"
    require(skill.is_file(), "Cannot find the bundled SKILL.md")
    root.mkdir(parents=True, exist_ok=False)
    for directory in ("artifacts", "derived", "scripts", "logs", "inbox", "evidence"):
        (root / directory).mkdir()
    shutil.copyfile(source, root / "are.py")
    shutil.copyfile(skill, root / "SKILL.md")
    (root / "goal.md").write_text(f"# Goal\n\n{args.goal}\n\n## Context and constraints\n\n"
                                "Record target identity, available access, scope, and non-goals here.\n")
    (root / "wiki.md").write_text("# Findings\n\n## Facts\n\n## Hypotheses\n\n"
                                "## Disproved\n\n## Unknowns\n")
    (root / "inbox/REQUESTS.md").write_text("# Requested resources\n\n"
                                         "Name the needed file and the question it unblocks.\n")
    (root / "attempts.jsonl").touch()
    write(root / "plan.json", {"action": "continue", "paths": [
        {"id": "triage", "priority": 1, "status": "ready",
         "question": args.goal, "blocked_on": []}]})
    write(root / "run.json", {"version": 1, "status": "ready", "turns": 0,
                             "max_turns": args.max_turns, "timeout": args.timeout,
                             "verify": command, "inputs": {}, "reason": ""})


def record(args, root):
    with lock(root, ".attempts.lock"):
        count = attempts(root)
        for text in (args.hypothesis, args.method, args.outcome):
            require(text.strip(), "Hypothesis, method, and outcome cannot be empty")
        identity = f"ATTEMPT-{count + 1:04d}"
        destination = local(root, f"evidence/{identity}")
        require(not destination.exists(), f"Uncommitted evidence exists: {destination}")
        sources = [local(root, name) for name in args.evidence]
        hashes = [digest(path) for path in sources]
        destination.mkdir()
        evidence = []
        for index, (name, source) in enumerate(zip(args.evidence, sources)):
            snapshot = destination / f"{index:02d}-{source.name}"
            shutil.copyfile(source, snapshot)
            sha = digest(snapshot)
            require(sha == hashes[index], f"Evidence changed while recording: {name}")
            evidence.append({"source": name, "snapshot": str(snapshot.relative_to(root)),
                             "sha256": sha})
        row = {"id": identity, "timestamp": datetime.now(timezone.utc).isoformat(),
               "hypothesis": args.hypothesis, "method": args.method,
               "outcome": args.outcome, "kind": args.kind, "evidence": evidence,
               "limitations": args.limitations}
        row["sha256"] = seal(row)
        with (root / "attempts.jsonl").open("a") as stream:
            stream.write(json.dumps(row) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        print(identity)


def run(args, root, value):
    command = args.agent[1:] if args.agent[:1] == ["--"] else args.agent
    require(command, "Pass a noninteractive agent command after --")
    while True:
        new_inputs = inspect(root, value)
        if value["status"] == "complete":
            receipt = value.get("verification", {})
            require(isinstance(receipt, dict) and not new_inputs
                    and receipt.get("exit_code") == 0
                    and receipt.get("command") == value["verify"]
                    and receipt.get("goal_sha256") == digest(root / "goal.md")
                    and receipt.get("outputs") == files(root, ("derived", "scripts"))
                    and digest(local(root, receipt.get("log"))) == receipt.get("sha256"),
                    "Completion is stale; review the changes and run verify again")
            return 0
        agenda = plan(root)
        if agenda["action"] == "verify":
            if verify(root, value) == 0:
                return 0
            agenda["action"] = "continue"
            repair = next((item for item in agenda["paths"] if item["id"] == "acceptance"), None)
            if repair is None:
                repair = {"id": "acceptance", "priority": 1,
                          "question": "Resolve the failed acceptance check", "blocked_on": []}
                agenda["paths"].append(repair)
            repair["status"] = "ready"
            write(root / "plan.json", agenda)
        ready = sorted((item for item in agenda["paths"] if item["status"] == "ready"),
                       key=lambda item: (item["priority"], item["id"]))
        if not ready:
            value["status"] = "waiting"
            value["reason"] = "No ready paths; supply requested inbox files and run again"
            write(root / "run.json", value)
            return 0
        if value["turns"] >= value["max_turns"]:
            value["status"] = "exhausted"
            value["reason"] = "Turn budget reached"
            write(root / "run.json", value)
            return 2
        value["turns"] += 1
        value["status"] = "running"
        write(root / "run.json", value)
        prompt = (root / "SKILL.md").read_text() + (
            "\n\nThis project is already initialized. Work here for one investigation pass. "
            "Do not start another runner. Read goal.md, plan.json, wiki.md, and attempts.jsonl. "
            f"Prioritize path {ready[0]['id']}: {ready[0]['question']}. "
            f"Previous result: {value.get('reason', '')}. "
            "Use python3 are.py record . to save evidence. "
            "Update plan.json; set action to verify only when the acceptance check is ready."
        )
        log = root / "logs" / f"turn-{value['turns']:04d}.log"
        print(f"Turn {value['turns']}/{value['max_turns']}: {log}", flush=True)
        code = invoke(root, [*command, prompt], log, value["timeout"])
        inspect(root, value)
        require(code == 0, f"Agent exited {code}; see {log.relative_to(root)}")
        value["reason"] = f"Agent pass finished; see {log.relative_to(root)}"
        write(root / "run.json", value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    start = commands.add_parser("init", help="Create a self-contained target workspace")
    start.add_argument("project", type=Path)
    start.add_argument("--goal", required=True)
    start.add_argument("--verify", required=True, help="Command string; parsed without a shell")
    start.add_argument("--max-turns", type=int, default=20)
    start.add_argument("--timeout", type=int, default=900, help="Seconds per agent/check invocation")
    note = commands.add_parser("record", help="Snapshot evidence and append one canonical attempt")
    note.add_argument("project", type=Path)
    for field in ("hypothesis", "method", "outcome"):
        note.add_argument(f"--{field}", required=True)
    note.add_argument("--kind", choices=("observed", "derived", "inferred"), required=True)
    note.add_argument("--evidence", action="append", required=True, help="Project-relative file; repeatable")
    note.add_argument("--limitations", default="")
    runner = commands.add_parser("run", help="Run bounded passes and stop on completion or blocks")
    runner.add_argument("project", type=Path)
    runner.add_argument("agent", nargs=argparse.REMAINDER)
    check = commands.add_parser("verify", help="Check evidence integrity and run the acceptance command")
    check.add_argument("project", type=Path)
    args = parser.parse_args()
    root = args.project.resolve()
    if args.operation in {"run", "verify"}:
        for stop in (signal.SIGTERM, signal.SIGHUP):
            signal.signal(stop, signal.default_int_handler)
    try:
        if args.operation == "init":
            init(args, root)
            print(root)
            return 0
        if args.operation == "record":
            record(args, root)
            return 0
        with lock(root, ".run.lock"):
            value = state(root)
            try:
                if args.operation == "run":
                    return run(args, root, value)
                return int(verify(root, value) != 0)
            except KeyboardInterrupt:
                value["status"] = "interrupted"
                value["reason"] = "Interrupted; run again to resume within the remaining budget"
                write(root / "run.json", value)
                return 130
            except (OSError, ValueError, subprocess.TimeoutExpired) as error:
                value["status"] = "failed"
                value["reason"] = str(error)
                write(root / "run.json", value)
                raise
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"are: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
