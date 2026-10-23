"""Probe reporting/negative controls only; fakes here do NOT prove provider flow."""

from contextlib import ExitStack, redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import jot_agent
import jot_evaluator


_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "probe-evaluator.py"
_SPEC = importlib.util.spec_from_file_location("jot_evaluator_probe", _SCRIPT)
_PROBE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PROBE)


class EvaluatorProbeTests(unittest.TestCase):
    def test_no_opt_in_starts_no_evaluator(self):
        result = subprocess.run([sys.executable, str(_SCRIPT), "unused.md", "--evaluator", "codex"], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"--allow-provider-call is required", result.stderr)
        self.assertEqual(result.stdout, b"")

    def test_output_directory_failure_is_named_without_traceback(self):
        with tempfile.TemporaryDirectory() as temporary:
            occupied = Path(temporary) / "PRIVATE_SECRET"
            occupied.write_text("not a directory")
            with redirect_stdout(io.StringIO()) as stream:
                code = _PROBE.main(["unused.md", "--evaluator", "codex", "--allow-provider-call", "--output-dir", str(occupied)])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stream.getvalue())["hop"], "artifact_storage")
        self.assertNotIn("PRIVATE_SECRET", stream.getvalue())

    def test_missing_real_cli_names_first_hop(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"PATH": ""}), redirect_stdout(io.StringIO()) as stream:
            code = _PROBE.probe(Path(directory) / "unused.md", "codex", Path(directory))
        records = [json.loads(line) for line in stream.getvalue().splitlines()]
        self.assertEqual(code, 1)
        self.assertEqual(records[-1]["hop"], "native_cli")
        self.assertEqual(records[-1]["status"], "FAIL")
        self.assertEqual(records[-1]["native_invocations"], 0)
        self.assertFalse(any(r["status"] == "PASS" for r in records))

    def test_safe_native_summary_never_echoes_unknown_values(self):
        events = [{"type": "PRIVATE_SECRET"}, {"type": ["PRIVATE_SECRET"]}, {"type": "item.completed", "item": {"type": "error", "message": "PRIVATE_SECRET"}}, {"type": "turn.completed"}]
        summary = _PROBE.native_summary(("\n".join(json.dumps(e) for e in events) + "\nPRIVATE_SECRET").encode(), "codex")
        self.assertEqual(summary["events"]["item_error"], 1)
        self.assertEqual(summary["events"]["turn.completed"], 1)
        self.assertEqual(summary["events"]["unknown"], 2)
        self.assertEqual(summary["events"]["invalid_json"], 1)
        self.assertNotIn("PRIVATE_SECRET", json.dumps(summary))
        self.assertNotIn("PRIVATE_SECRET", json.dumps(_PROBE.native_summary(b'{"structured_output": {"x":"PRIVATE_SECRET"}}', "claude")))

    def test_real_preinvoke_failures_keep_source_request_stage(self):
        for failure in ("reload", "lookup", "discovery"):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as temporary:
                import jot

                directory = Path(temporary)
                source = directory / "source.md"
                source.write_text(jot._build_transcript_markdown(
                    {"title": "Fixture", "channel": "Fixture", "duration": 20},
                    "[00:04] PRIVATE_SECRET", "https://www.youtube.com/watch?v=WkBPX-oDMnA", "Fixture",
                ))
                read_text = Path.read_text

                def reload(path, *args, **kwargs):
                    if path.name.endswith(".request.json"):
                        raise ValueError("PRIVATE_SECRET")
                    return read_text(path, *args, **kwargs)

                with ExitStack() as stack, redirect_stdout(io.StringIO()) as stream:
                    discovery = stack.enter_context(patch.object(
                        jot_evaluator, "find_evaluator",
                        side_effect=["synthetic-cli", ValueError("PRIVATE_SECRET")],
                    ))
                    runner = stack.enter_context(patch.object(
                        jot_evaluator, "_run_evaluator", return_value=(b"codex-cli 0.163.0\n", 0),
                    ))
                    stack.enter_context(patch.object(subprocess, "Popen", side_effect=AssertionError("process forbidden")))
                    if failure == "reload":
                        stack.enter_context(patch.object(Path, "read_text", reload))
                    elif failure == "lookup":
                        stack.enter_context(patch.object(jot_agent, "_source_catalog", side_effect=ValueError("PRIVATE_SECRET")))
                    code = _PROBE.probe(source, "codex", directory)
                records = [json.loads(line) for line in stream.getvalue().splitlines()]
                self.assertEqual(code, 1)
                self.assertEqual(records[-1]["hop"], "native_process" if failure == "discovery" else "source_request")
                self.assertEqual(records[-1]["status"], "FAIL")
                self.assertEqual(records[-1]["native_invocations"], 0)
                self.assertTrue(any(r["hop"] == "source_request" and r["status"] == "PASS" for r in records))
                self.assertEqual(len(list(directory.glob("*.request.json"))), 1)
                runner.assert_called_once()
                self.assertEqual(runner.call_args.args[0], ["synthetic-cli", "--version"])
                self.assertEqual(discovery.call_count, 2 if failure == "discovery" else 1)
                self.assertNotIn("PRIVATE_SECRET", stream.getvalue())

    def test_observer_hops_and_failure_privacy(self):
        for mode, expected_hop in (("process", "native_process"), ("decode", "native_decode"), ("validate", "local_validation"), ("empty", "publication"), ("bypass", "source_request"), ("bypass_validation", "local_validation"), ("summary", "result"), ("success", "result")):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                request = directory / "request.json"
                request.write_text('{"private":"PRIVATE_SECRET"}')
                markdown = directory / "report.md"
                html = directory / "report.html"
                markdown.write_text("synthetic markdown")
                html.write_text("" if mode == "empty" else "synthetic html")

                def fake_runner(command, *args, **kwargs):
                    if command[-1] == "--version":
                        return b"codex-cli 0.163.0\n", 0
                    return b'{"type":"turn.completed"}\n', 7 if mode == "process" else 0

                def fake_invoke(*args, **kwargs):
                    jot_evaluator._run_evaluator(["synthetic-cli", "exec"], b"", directory, {})
                    if mode == "decode":
                        raise ValueError("PRIVATE_SECRET")
                    return {"private": "PRIVATE_SECRET"}

                def fake_validate(*args, **kwargs):
                    if mode == "validate":
                        raise ValueError("PRIVATE_SECRET")
                    return None

                def fake_evaluate(*args, **kwargs):
                    if mode == "bypass":
                        return markdown, html
                    jot_agent.prepare_evaluation(None)
                    jot_evaluator.invoke_evaluator(None, None)
                    if mode != "bypass_validation":
                        jot_agent._validate(None, None)
                    return markdown, html

                with ExitStack() as stack, redirect_stdout(io.StringIO()) as stream:
                    for owner, name, replacement in ((jot_evaluator, "find_evaluator", lambda _: "synthetic-cli"), (jot_evaluator, "_run_evaluator", fake_runner), (jot_agent, "prepare_evaluation", lambda *args, **kwargs: request), (jot_evaluator, "invoke_evaluator", fake_invoke), (jot_agent, "_validate", fake_validate), (jot_agent, "evaluate_transcript", fake_evaluate)):
                        stack.enter_context(patch.object(owner, name, replacement))
                    if mode == "summary":
                        stack.enter_context(patch.object(_PROBE, "native_summary", side_effect=ValueError("PRIVATE_SECRET")))
                    code = _PROBE.probe(directory / "source.md", "codex", directory)
                records = [json.loads(line) for line in stream.getvalue().splitlines()]
                self.assertEqual(code, 0 if mode in ("success", "summary") else 1)
                self.assertEqual(records[-1]["hop"], expected_hop)
                self.assertEqual(records[-1]["status"], "PASS" if mode in ("success", "summary") else "FAIL")
                self.assertNotIn("PRIVATE_SECRET", stream.getvalue())
                self.assertTrue(any(r["hop"] == "native_exec_effective_skill_catalog" and r["status"] == "UNOBSERVED" for r in records))


if __name__ == "__main__":
    unittest.main()
