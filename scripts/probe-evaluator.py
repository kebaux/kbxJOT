#!/usr/bin/env python3
"""Probe a saved transcript -> native evaluator -> validated HTML, once.

Run: uv run python scripts/probe-evaluator.py SOURCE --evaluator codex \
         --allow-provider-call [--output-dir DIR]
Requires explicit usage/credits consent; never retries or repairs evidence. Writes
only temporary artifacts unless --output-dir is supplied. JSONL contains bounded
counts/statuses, never provider messages, source text, stderr or authentication.
A successful run proves this report path, NOT host-skill isolation or factual truth.
"""

import argparse
from contextlib import ExitStack
import json
import os
from pathlib import Path
import re
import sys
import subprocess
import tempfile
import time
from unittest.mock import patch

# Support direct execution from any cwd without installing this development tool.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


HOPS = (
    {"name": "native_cli", "kind": "process", "observe": "resolved executable runs --version"},
    {"name": "source_request", "kind": "filesystem/serialization", "observe": "real request preparation returns nonempty artifact"},
    {"name": "native_process", "kind": "process/provider/time", "observe": "real contained runner status, byte count, event counters"},
    {"name": "native_decode", "kind": "serialization", "observe": "real evaluator adapter returns an object"},
    {"name": "local_validation", "kind": "source/serialization", "observe": "real full source/schema/evidence validator returns"},
    {"name": "publication", "kind": "filesystem", "observe": "real publisher returns nonempty Markdown and HTML artifacts"},
)


def native_summary(stdout, evaluator):
    """Count only known protocol facts; arbitrary event names/messages stay private."""
    summary = {"stdout_bytes": len(stdout)}
    if evaluator == "claude":
        try:
            envelope = json.loads(stdout)
        except (ValueError, UnicodeError):
            return {**summary, "envelope_json": False}
        return {**summary, "envelope_json": True,
                "structured_output_object": isinstance(envelope, dict) and isinstance(envelope.get("structured_output"), dict),
                "is_error": isinstance(envelope, dict) and envelope.get("is_error") is True}
    counts = {name: 0 for name in ("thread.started", "turn.started", "turn.completed", "turn.failed", "error", "agent_message", "item_error", "unknown", "invalid_json")}
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except (ValueError, UnicodeError):
            counts["invalid_json"] += 1
            continue
        kind = event.get("type") if isinstance(event, dict) else None
        if kind in ("thread.started", "turn.started", "turn.completed", "turn.failed", "error"):
            counts[kind] += 1
        elif kind in ("item.started", "item.updated", "item.completed"):
            item = event.get("item")
            if kind == "item.completed" and isinstance(item, dict):
                if item.get("type") == "error":
                    counts["item_error"] += 1
                elif item.get("type") == "agent_message":
                    counts["agent_message"] += 1
        else:
            counts["unknown"] += 1
    return {**summary, "events": counts}


def probe(source, evaluator, output_dir):
    """Delegate once to the product flow; report its first failing hop safely.

    Wrappers observe actual delegates, never replace native bytes or validation.
    Private hooks are intentionally local to this development diagnostic; tests
    of the wrappers are not evidence that a native/provider boundary was crossed.
    """
    started = time.monotonic()
    stage = "native_cli"
    calls = 0
    observed = set()

    def report(hop, status, **evidence):
        if status == "PASS":
            observed.add(hop)
        print(json.dumps({"hop": hop, "status": status, "elapsed_seconds": round(time.monotonic() - started, 3), **evidence}, sort_keys=True), flush=True)

    report("inventory", "INFO", evaluator=evaluator, hops=HOPS)
    report("native_exec_effective_skill_catalog", "UNOBSERVED", reason="No equivalent nonbillable exec catalog interface established; flags and adjacent app-server catalog RPC do not prove isolation.")
    report("provider_internals", "UNOBSERVED", reason="Only native process output is observable; provider-side prompt, tools and skill selection are not.")
    try:
        import jot_agent
        import jot_evaluator

        executable = jot_evaluator.find_evaluator(evaluator)
        environment = {k: v for k, v in os.environ.items() if k not in jot_evaluator._SESSION_ENV_VARS}
        version_bytes, version_code = jot_evaluator._run_evaluator([executable, "--version"], b"", output_dir, environment, timeout=10)
        if version_code != 0 or not version_bytes.strip():
            raise ValueError("version unavailable")
        version = re.search(rb"\b[0-9]+\.[0-9]+\.[0-9]+\b", version_bytes)
        if version is None:
            raise ValueError("unrecognized version")
        report(stage, "PASS", version=version.group().decode("ascii"), returncode=version_code)

        prepare = jot_agent.prepare_evaluation
        run = jot_evaluator._run_evaluator
        invoke = jot_evaluator.invoke_evaluator
        validate = jot_agent._validate

        def observed_prepare(*args, **kwargs):
            nonlocal stage
            stage = "source_request"
            request = prepare(*args, **kwargs)
            size = request.stat().st_size
            if size == 0:
                raise ValueError("empty request")
            report(stage, "PASS", request_bytes=size)
            stage = "native_process"
            return request

        def observed_run(*args, **kwargs):
            nonlocal stage, calls
            stage = "native_process"
            calls += 1
            if calls != 1:
                raise ValueError("unexpected extra native invocation")
            stdout, returncode = run(*args, **kwargs)
            try:
                summary = native_summary(stdout, evaluator)
            except Exception:
                # A diagnostic parser must not replace the real adapter's verdict.
                summary = {"stdout_bytes": len(stdout), "summary_unavailable": True}
            evidence = {"returncode": returncode, **summary}
            if returncode != 0:
                report(stage, "OBSERVED", **evidence)
                raise ValueError("native process failed")
            report(stage, "PASS", **evidence)
            stage = "native_decode"
            return stdout, returncode

        def observed_invoke(*args, **kwargs):
            nonlocal stage
            response = invoke(*args, **kwargs)
            stage = "native_decode"
            if not isinstance(response, dict):
                raise ValueError("nonobject response")
            report(stage, "PASS", response_object=True)
            # Product saves the raw response before validating/publishing it.
            stage = "publication"
            return response

        def observed_validate(*args, **kwargs):
            nonlocal stage
            stage = "local_validation"
            result = validate(*args, **kwargs)
            report(stage, "PASS")
            stage = "publication"
            return result

        stage = "source_request"
        with ExitStack() as stack:
            for owner, name, observer in ((jot_agent, "prepare_evaluation", observed_prepare), (jot_evaluator, "_run_evaluator", observed_run), (jot_evaluator, "invoke_evaluator", observed_invoke), (jot_agent, "_validate", observed_validate)):
                stack.enter_context(patch.object(owner, name, observer))
            markdown, html = jot_agent.evaluate_transcript(source, output_dir=output_dir, evaluator=evaluator)
        missing = [hop["name"] for hop in HOPS[:-1] if hop["name"] not in observed]
        if missing:
            report(missing[0], "FAIL", category="missing_observation", native_invocations=calls)
            return 1
        stage = "publication"
        sizes = [path.stat().st_size for path in (markdown, html)]
        if calls != 1 or not all(sizes):
            raise ValueError("missing invocation or artifacts")
        report(stage, "PASS", markdown_bytes=sizes[0], html_bytes=sizes[1])
        report("result", "PASS", native_invocations=calls, scope="saved transcript produced validated HTML; catalog isolation remains unobserved")
        return 0
    except KeyboardInterrupt:
        report(stage, "FAIL", category="cancelled", native_invocations=calls)
        return 130
    except Exception as exc:
        # Exception messages/tracebacks can contain source quotes, paths or secrets.
        category = next((label for cls, label in ((FileNotFoundError, "missing_file"), ((TimeoutError, subprocess.TimeoutExpired), "timeout"), (OSError, "os_error"), (ValueError, "invalid_or_rejected")) if isinstance(exc, cls)), "unexpected_error")
        report(stage, "FAIL", category=category, native_invocations=calls)
        return 1


def main(argv=None):
    """Require explicit billing consent; temporary output is the safe default."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--evaluator", required=True, choices=("codex", "claude"))
    parser.add_argument("--allow-provider-call", action="store_true", help="Confirm permission for one real evaluation consuming usage/credits; no retries.")
    parser.add_argument("--output-dir", type=Path, help="Preserve new request/response/report files here; otherwise delete temporary artifacts on exit.")
    args = parser.parse_args(argv)
    if not args.allow_provider_call:
        parser.error("--allow-provider-call is required; this probe consumes evaluator usage/credits")
    try:
        with tempfile.TemporaryDirectory(prefix="jot-evaluator-probe-") as temporary:
            directory = args.output_dir.expanduser().resolve() if args.output_dir is not None else Path(temporary)
            directory.mkdir(parents=True, exist_ok=True)
            return probe(args.source.expanduser().resolve(), args.evaluator, directory)
    except KeyboardInterrupt:
        print(json.dumps({"hop": "artifact_storage", "status": "FAIL", "category": "cancelled"}), flush=True)
        return 130
    except (OSError, ValueError, RuntimeError):
        print(json.dumps({"hop": "artifact_storage", "status": "FAIL", "category": "setup_or_cleanup_failed"}), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
