"""Exercise the public CLI with synthetic frames and controlled agent processes."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest

TOOL = Path(__file__).resolve().parents[1] / "scripts/are.py"
DECODER = """def decode(frame):
    if (len(frame) != 6 or frame[0] != 0xa5 or frame[1] != 3
            or sum(frame[:-1]) & 255 != frame[-1]):
        raise ValueError("invalid frame")
    return frame[2], int.from_bytes(frame[3:5], "little")
"""
CHECKER = """import importlib.util
spec = importlib.util.spec_from_file_location("decoder", "derived/decoder.py")
decoder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(decoder)
for raw, expected in [
    ("a503103412fe", (16, 4660)),
    ("a50320ff00c7", (32, 255)),
    ("a50310008038", (16, 32768)),
]:
    assert decoder.decode(bytes.fromhex(raw)) == expected
for raw in ["", "a503103412", "0003103412fe", "a50310341200"]:
    try:
        decoder.decode(bytes.fromhex(raw))
    except ValueError:
        continue
    raise AssertionError("malformed frame accepted")
print("3 reference frames and 4 malformed cases passed")
"""
AGENT_PREFIX = """from pathlib import Path
import json, subprocess, sys
calls = Path("logs/calls.txt")
calls.write_text(calls.read_text() + "call\\n" if calls.exists() else "call\\n")
"""
FINISH = """subprocess.run([
    sys.executable, "are.py", "record", ".",
    "--hypothesis", "Payload is a little-endian integer",
    "--method", "Decode saved frame and compare with the reference",
    "--outcome", "Candidate decoder saved",
    "--kind", "derived", "--evidence", "derived/decoder.py"
], check=True)
agenda = json.loads(Path("plan.json").read_text())
agenda["action"] = "verify"
for path in agenda["paths"]:
    path["status"] = "done"
Path("plan.json").write_text(json.dumps(agenda))
"""


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="are-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.project = self.base / "project with spaces"
        self.cli("init", self.project, "--goal", "Recover the synthetic frame format",
                 "--verify", f"{shlex.quote(sys.executable)} scripts/check.py",
                 "--max-turns", "2", "--timeout", "1")
        (self.project / "artifacts/frame.hex").write_text("a503103412fe\n")
        (self.project / "scripts/check.py").write_text(CHECKER)

    def cli(self, *arguments, expected=0):
        result = subprocess.run([sys.executable, str(TOOL), *map(str, arguments)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def get(self, name="run.json"):
        return json.loads((self.project / name).read_text())

    def put(self, name, value):
        (self.project / name).write_text(json.dumps(value))

    def agent(self, body):
        path = self.base / "agent stub.py"
        path.write_text(AGENT_PREFIX + body)
        return path

    def completing_agent(self, decoder=DECODER):
        return self.agent(f'Path("derived/decoder.py").write_text({decoder!r})\n' + FINISH)

    def run_agent(self, agent, expected=0):
        return self.cli("run", self.project, "--", sys.executable, agent, expected=expected)

    def calls(self):
        path = self.project / "logs/calls.txt"
        return path.read_text().count("call\n") if path.exists() else 0

    def record(self, source="artifacts/frame.hex", expected=0):
        return self.cli("record", self.project, "--hypothesis", "Frame has a checksum",
                        "--method", "Inspect saved bytes", "--outcome", "Bytes retained",
                        "--kind", "observed", "--evidence", source, expected=expected)

    def test_initialized_workspace_is_portable_and_never_overwritten(self):
        result = self.cli("init", self.project, "--goal", "overwrite", "--verify", "true", expected=1)
        self.assertIn("File exists", result.stderr)
        self.assertIn("Recover the synthetic", (self.project / "goal.md").read_text())
        portable = self.base / "nested"
        subprocess.run([sys.executable, str(self.project / "are.py"), "init", str(portable),
                        "--goal", "new goal", "--verify", "true"], check=True, capture_output=True)
        self.assertEqual((portable / "SKILL.md").read_bytes(), (self.project / "SKILL.md").read_bytes())

    def test_invalid_budget_and_empty_checker_create_nothing(self):
        for options in [("--max-turns", "0"), ("--timeout", "-1"), ("--verify", "")]:
            with self.subTest(options=options):
                path = self.base / "invalid"
                self.cli("init", path, "--goal", "goal", "--verify", "true", *options, expected=1)
                self.assertFalse(path.exists())

    def test_decoder_passes_reference_and_malformed_cases_without_restarting(self):
        agent = self.completing_agent()
        self.run_agent(agent)
        receipt = self.get()
        self.assertEqual(receipt["status"], "complete")
        self.assertEqual(receipt["turns"], 1)
        verification = receipt["verification"]
        self.assertIn("3 reference frames", (self.project / verification["log"]).read_text())
        self.assertIn("derived/decoder.py", verification["outputs"])
        self.run_agent(agent)
        self.assertEqual(self.calls(), 1)

    def test_failed_acceptance_returns_to_investigation_and_can_be_fixed(self):
        wrong = DECODER.replace('"little"', '"big"')
        agent = self.agent(
            f"decoder = {wrong!r} if calls.read_text().count('call\\n') == 1 else {DECODER!r}\n"
            'Path("derived/decoder.py").write_text(decoder)\n' + FINISH)
        self.run_agent(agent)
        self.assertEqual(self.get()["status"], "complete")
        self.assertEqual(self.calls(), 2)
        logs = list((self.project / "logs").glob("verify-*.log"))
        self.assertEqual(len(logs), 2)
        self.assertTrue(any("AssertionError" in path.read_text() for path in logs))
        self.assertEqual(len((self.project / "attempts.jsonl").read_text().splitlines()), 2)

    def test_wrong_decoder_never_claims_completion(self):
        self.run_agent(self.completing_agent(DECODER.replace('"little"', '"big"')), expected=2)
        self.assertEqual(self.get()["status"], "exhausted")
        self.assertNotIn("verification", self.get())
        self.assertEqual(self.calls(), 2)

    def test_completion_requires_recorded_evidence(self):
        agent = self.agent(f'Path("derived/decoder.py").write_text({DECODER!r})\n'
                           'agenda = json.loads(Path("plan.json").read_text())\n'
                           'agenda["action"] = "verify"\n'
                           'Path("plan.json").write_text(json.dumps(agenda))\n')
        result = self.run_agent(agent, expected=1)
        self.assertIn("Record evidence", result.stderr)
        self.assertEqual(self.get()["status"], "failed")
        self.assertEqual(self.calls(), 1)

    def test_turn_budget_survives_another_run(self):
        agent = self.agent("pass\n")
        self.run_agent(agent, expected=2)
        self.run_agent(agent, expected=2)
        self.assertEqual(self.get()["turns"], 2)
        self.assertEqual(self.calls(), 2)

    def test_agent_execution_error_is_not_retried(self):
        result = self.run_agent(self.agent('print("tool failed"); sys.exit(23)\n'), expected=1)
        self.assertIn("Agent exited 23", result.stderr)
        self.assertEqual(self.get()["status"], "failed")
        self.assertEqual(self.calls(), 1)

    def test_agent_cannot_modify_original_inputs(self):
        result = self.run_agent(self.agent('Path("artifacts/frame.hex").write_text("changed")\n'),
                                expected=1)
        self.assertIn("Input changed", result.stderr)
        self.assertEqual(self.get()["status"], "failed")

    def test_changed_and_missing_pinned_inputs_are_rejected(self):
        agent = self.completing_agent()
        self.run_agent(agent)
        path = self.project / "artifacts/frame.hex"
        original = path.read_bytes()
        path.write_text("changed")
        self.assertIn("Input changed", self.run_agent(agent, expected=1).stderr)
        path.write_bytes(original)
        path.unlink()
        self.assertIn("disappeared", self.run_agent(agent, expected=1).stderr)
        self.assertEqual(self.calls(), 1)

    def test_snapshots_preserve_old_outputs_and_detect_tampering(self):
        path = self.project / "derived/probe.txt"
        path.write_text("first observation")
        self.record("derived/probe.txt")
        path.write_text("later output")
        self.record("derived/probe.txt")
        rows = [json.loads(line) for line in (self.project / "attempts.jsonl").read_text().splitlines()]
        first = self.project / rows[0]["evidence"][0]["snapshot"]
        self.assertEqual(first.read_text(), "first observation")
        self.assertEqual(rows[0]["evidence"][0]["sha256"], hashlib.sha256(first.read_bytes()).hexdigest())
        first.write_text("forged")
        result = self.record(expected=1)
        self.assertIn("Evidence changed", result.stderr)
        self.assertEqual(len((self.project / "attempts.jsonl").read_text().splitlines()), 2)

    def test_attempt_metadata_tampering_is_rejected(self):
        self.record()
        row = json.loads((self.project / "attempts.jsonl").read_text())
        row["outcome"] = "invented certainty"
        (self.project / "attempts.jsonl").write_text(json.dumps(row) + "\n")
        self.assertIn("Attempt record changed", self.record(expected=1).stderr)

    def test_missing_or_outside_evidence_does_not_commit_an_attempt(self):
        for name in ("logs/missing.txt", "../outside", str(self.base / "outside")):
            with self.subTest(name=name):
                self.record(name, expected=1)
                self.assertEqual((self.project / "attempts.jsonl").read_text(), "")
                self.assertEqual(list((self.project / "evidence").iterdir()), [])

    def test_waiting_does_not_consume_turns_and_inbox_arrival_unblocks(self):
        agenda = self.get("plan.json")
        agenda["paths"][0].update(status="blocked", blocked_on=["inbox/capture.hex"])
        self.put("plan.json", agenda)
        agent = self.completing_agent()
        self.run_agent(agent)
        self.assertEqual(self.get()["status"], "waiting")
        self.assertEqual(self.get()["turns"], 0)
        (self.project / "inbox/REQUESTS.md").write_text("Please supply capture.hex")
        self.run_agent(agent)
        self.assertEqual(self.calls(), 0)
        (self.project / "inbox/capture.hex").write_text("a50320ff00c7")
        self.run_agent(agent)
        self.assertEqual(self.get()["status"], "complete")
        self.assertEqual(self.get()["turns"], 1)
        self.assertIn("inbox/capture.hex", self.get()["inputs"])

    def test_malformed_plan_never_invokes_agent(self):
        original = self.get("plan.json")
        for item in [
            {"action": "unknown", "paths": []},
            {"action": [], "paths": []},
            {"action": "continue", "paths": [{"id": "bad", "priority": True}]},
            {"action": "continue", "paths": [{**original["paths"][0], "blocked_on": ["../escape"]}]},
        ]:
            with self.subTest(item=item):
                self.put("plan.json", item)
                self.run_agent(self.agent("pass\n"), expected=1)
                self.assertEqual(self.calls(), 0)

    def test_goal_and_acceptance_command_changes_invalidate_completion(self):
        agent = self.completing_agent()
        self.run_agent(agent)
        goal = self.project / "goal.md"
        original = goal.read_text()
        goal.write_text(original + "A new requirement\n")
        self.assertIn("Completion is stale", self.run_agent(agent, expected=1).stderr)
        goal.write_text(original)
        self.cli("verify", self.project)
        changed = self.get()
        changed["verify"].append("new-case")
        self.put("run.json", changed)
        self.assertIn("Completion is stale", self.run_agent(agent, expected=1).stderr)
        self.assertEqual(self.calls(), 1)

    def test_goal_cannot_change_during_acceptance(self):
        (self.project / "scripts/check.py").write_text(
            'from pathlib import Path\nPath("goal.md").write_text("a different goal")\n')
        result = self.run_agent(self.completing_agent(), expected=1)
        self.assertIn("Goal changed during acceptance", result.stderr)
        self.assertEqual(self.get()["status"], "failed")
        self.assertNotIn("verification", self.get())

    def test_symlinked_input_directory_is_not_traversed(self):
        directory = self.project / "artifacts"
        moved = self.base / "outside"
        directory.rename(moved)
        directory.symlink_to(moved, target_is_directory=True)
        result = self.run_agent(self.agent("pass\n"), expected=1)
        self.assertIn("Expected a project directory", result.stderr)
        self.assertEqual(self.calls(), 0)

    def test_malformed_run_state_has_a_bounded_diagnostic(self):
        invalid = self.get()
        invalid["status"] = []
        self.put("run.json", invalid)
        result = self.run_agent(self.agent("pass\n"), expected=1)
        self.assertIn("Invalid run status", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.calls(), 0)

    def test_stale_completed_outputs_and_new_inputs_require_review(self):
        agent = self.completing_agent()
        self.run_agent(agent)
        (self.project / "derived/decoder.py").write_text(DECODER.replace('"little"', '"big"'))
        self.assertIn("Completion is stale", self.run_agent(agent, expected=1).stderr)
        self.cli("verify", self.project, expected=1)
        self.assertEqual(self.get()["status"], "ready")
        (self.project / "derived/decoder.py").write_text(DECODER)
        self.cli("verify", self.project)
        (self.project / "inbox/new.hex").write_text("new input")
        self.assertIn("Completion is stale", self.run_agent(agent, expected=1).stderr)
        self.assertEqual(self.calls(), 1)

    def test_record_lock_prevents_concurrent_corruption(self):
        import fcntl
        with (self.project / ".attempts.lock").open("a") as owner:
            fcntl.flock(owner, fcntl.LOCK_EX)
            self.assertIn("Another writer", self.record(expected=1).stderr)
        self.record()
        self.assertEqual(len((self.project / "attempts.jsonl").read_text().splitlines()), 1)

    def test_run_lock_prevents_duplicate_agents(self):
        import fcntl
        with (self.project / ".run.lock").open("a") as owner:
            fcntl.flock(owner, fcntl.LOCK_EX)
            self.assertIn("Another writer", self.run_agent(self.agent("pass\n"), expected=1).stderr)
        self.assertEqual(self.calls(), 0)

    def test_acceptance_command_does_not_evaluate_shell_syntax(self):
        command = self.get()
        command["verify"].append("$(touch injected)")
        self.put("run.json", command)
        self.run_agent(self.completing_agent())
        self.assertFalse((self.project / "injected").exists())

    def test_deadline_stops_the_agent_and_its_background_child(self):
        agent = self.agent(
            'import time\n'
            'child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])\n'
            'Path("logs/child.pid").write_text(str(child.pid))\n'
            'time.sleep(30)\n')
        sentinel = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"],
                                    start_new_session=True)
        try:
            self.run_agent(agent, expected=1)
            self.assertEqual(self.get()["status"], "failed")
            self.assertIn("Deadline", self.get()["reason"])
            self.assertEqual(self.calls(), 1)
            self.assertIsNone(sentinel.poll())
            pid = int((self.project / "logs/child.pid").read_text())
            status = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)],
                                    capture_output=True, text=True).stdout.strip()
            self.assertTrue(not status or status.startswith("Z"), status)
        finally:
            sentinel.kill()
            sentinel.wait()

    def test_interruption_is_saved_and_kills_the_agent(self):
        agent = self.agent('import time\nPath("logs/started").touch()\ntime.sleep(30)\n')
        config = self.get()
        config["max_turns"] = 3
        self.put("run.json", config)
        for stop in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            with self.subTest(signal=stop):
                started = self.project / "logs/started"
                started.unlink(missing_ok=True)
                process = subprocess.Popen([sys.executable, str(TOOL), "run", str(self.project),
                                            "--", sys.executable, str(agent)],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                try:
                    deadline = time.monotonic() + 5
                    while not started.exists() and time.monotonic() < deadline:
                        time.sleep(0.02)
                    self.assertTrue(started.exists())
                    process.send_signal(stop)
                    process.communicate(timeout=5)
                    self.assertEqual(process.returncode, 130)
                    self.assertEqual(self.get()["status"], "interrupted")
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.communicate()


if __name__ == "__main__":
    unittest.main()
