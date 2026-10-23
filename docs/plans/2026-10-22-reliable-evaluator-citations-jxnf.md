# Reliable evaluator citations and native warning handling

**Date:** 2026-10-22\
**Last updated:** 2026-10-23\
**ID:** jxnf\
**Summary:** Repair the two diagnosed evaluation failures without weakening publication, and make the native isolation boundary observable and honest.\
**Progress:** [execution log](<../progress/2026-10-22-reliable-evaluator-citations-jxnf.md>)
<!-- planned: 1222923 · branch: main -->

## Context and Motivation

The [RCA](<../rca/RCA-2026-10-22-fresh-machine-evaluation-failures.md>) establishes a model-produced adjacent-timestamp mismatch and incorrect treatment of documented Codex non-fatal error items. The historical measured runner was `/tmp/jot-triage-standalone.AYWSQP/bin/python` (CPython 3.12.15, declared project dependencies installed), an ephemeral investigation environment, not a required dependency. Reusable checkout commands below use `uv run python` from the repository root. No active Beads workspace exists (`bd where` reports no workspace); use this paired Markdown log. User authorized proceeding with the recommended repairs, not commits or changes to host credentials/configuration.

## Scope Boundary

### What We're Doing
- Accept non-fatal Codex item errors while preserving strict stream/turn/final-result failure checks; use privacy-safe stage diagnostics.
- Make new model citations source-entry IDs with locally derived timestamps and exact source text; preserve original raw responses.
- Retain strict support for saved version-1 request/response artifacts and existing rendered reports, explicitly versioning new requests.
- Document the unsupported exact-exec catalog observation and remaining host discovery. Ship a discoverable real evaluator-flow boundary probe with named hops, a negative control, and explicit live opt-in.
- Run focused regressions, full suite, and independent code review.

### What We're NOT Doing
- No auto-retry, neighbor timestamp correction, partial invalid report, or coordinator fallback: these weaken provenance or change cost policy.
- No host authentication/config changes, credential copying, CLI upgrades, or commits.
- No promised hard skill isolation based only on flags, no warning, or token counts. Narrow the contract if native catalog isolation cannot be demonstrated.
- No claim of recovered original-machine behavior from local mocks. Original full Codex stdout and original machine/version are unavailable. Billable full-video reruns require explicit consent; keep that verification unclaimed unless authorized.

## Later commit authorization

After the implementation and evidence above, the user invoked `/git-commit` and explicitly approved four logical commits plus feature-branch push and draft-PR review. The original no-commit implementation scope remains a historical authorization record; this later approval permits committing the completed work. Publishing progress and review-tool availability are recorded in the paired execution log.

## Native Verification Limits

- **Resolved catalog feasibility:** No supported exact-exec local catalog observation was established on Codex 0.163.0. `app-server` lacks `exec --ignore-user-config`, uses a distinct catalog operation, and saved-login startup routing may perform backend requests. Record catalog/prompt isolation as unobserved and narrow the documentation; do not build an adjacent path to claim isolation.
- **Live consent audit — three Codex evaluation-process launches total, not one:** (1) The initial one-evaluation-per-installed-evaluator allowance covered the first Codex launch (exit 1, 0.718s, zero stdout and no observed events). (2) After that failure the user separately explicitly approved one private-stderr diagnostic (exit 1, 0.322s, zero stdout and no observed events). (3) The exact same diagnostic command received a separate one-shot wider-filesystem tool approval; this third launch completed native turn, validation and HTML publication (exit 0, 64.356s, 107 IDs). There were no application-level automatic retries. Zero observed events in the first two launches does not reveal provider internals or establish billing; those are unobserved. CLI version checks are not evaluation launches.
- **Claude / present authority:** Claude was absent and had zero evaluation launches. Missing-Claude verification remains limited by executable availability, not permission to install or substitute providers. The historical call allowance and diagnostics approvals are exhausted records, **not authorization for fresh model runs now**.

## Architecture Decision: Versioned source-entry citations

**Choice:** New request version 2 uses an evaluator citation containing only a deterministic integer source-entry ID (e.g. `source_id`). Jot reconstructs the authoritative entry catalog from the source, resolves its quote and timestamp locally for rendering/range validation, and preserves the raw ID response on disk. Prefer ID-only citations rather than optional model-supplied substrings: exact original physical lines are already short in caption input. Preserve duplicate-time entries and genuinely untimed lines. The catalog is derived, never trusted from model output or modified packet data.

**Alternatives considered:** Continue prompting the model to copy pairs; repair timestamps by neighboring text; change generation schema only while leaving the request's declared schema inconsistent with its saved response.

**Rationale:** Prevent the diagnosed independent quote/timestamp mixup structurally, while retaining one auditable request/response protocol and refusing ambiguity.

**Reversibility:** One-way at the persisted protocol boundary. Keep the existing version-1 schema as a packaged legacy asset and validate its trusted schema/rubric/digest exactly; never silently reinterpret v1 as v2.

**Cost of being wrong:** Saved v2 packets and downstream callers would require another explicit version/migration; losing v1 support would strand existing audit artifacts.

**Revisit trigger:** Demonstrated need for long untimed-source excerpt selection; add exact substrings bound to IDs only if that need exists.

**Fitness checks:** New packets reject timestamp/quote citation objects, unknown/bool/negative IDs, forged schemas/lookup, out-of-range citations, and absent evidence where the schema requires it. Preserve valid empty takeaways/ranges and empty evidence for `not_observed` signals; do not invent a report-wide citation quota. Existing v1 wrong quotes/timestamps still fail and valid v1 artifacts still publish. Publication never mutates input response or writes outputs on validation failure. Stable IDs prevent independently mismatched fields, not selection of the wrong source entry or unsupported narrative claims.

## Non-Functional Baseline
- **Auth:** Native CLI login stays in place; no stored credentials are read or copied by new tooling.
- **Secrets:** Never echo arbitrary warning/event messages, transcript quotes, private skill contents, or authentication diagnostics. Reason codes, warning counts and aggregate catalog metadata suffice.
- **Logging:** Name decoding/schema/evidence failure stages; aggregate evidence failures with safe locations/counts. Runtime warnings do not bypass complete report validation.

## Phase 1: Repair the local generation-to-publication contract

**Goal:** New evaluations cannot mix quote and timestamp independently, valid completed Codex turns survive warnings, and legacy audit artifacts remain strictly usable.\
**Estimated effort:** M (implementation plus regression review).

### Tasks
- **1.1:** In [decoder](<../../jot_evaluator.py>), distinguish non-fatal item errors from fatal stream/turn events; expose bounded reason codes while preserving malformed/duplicate JSON, invalid UTF-8, nonzero exits, incomplete turns, and missing/invalid final objects as failures. Add regressions to [runtime tests](<../../tests/test_jot_evaluator.py>).
- **1.2:** In [agent](<../../jot_agent.py>), [schema](<../../jot_assets/evaluation-response.schema.json>), and [instructions](<../../jot_assets/evaluator-instructions.md>), implement version-2 ID citations and deterministic catalog resolution. Add a packaged legacy schema asset and include it in [package manifest](<../../pyproject.toml>). Preserve v1 trust checks and raw evidence; do not rewrite the incident files.
- **1.3:** Extend [agent tests](<../../tests/test_jot_agent.py>) for the 1907/1909 failure class, equal timestamps, repeated quotes, untimed input, range membership, type/unknown-ID attacks, exact version/schema/digest checks, aggregate privacy-safe failures, non-mutation and all-or-nothing publication. Preserve meaningful v1 regressions; do not weaken expected failures simply to turn the suite green.

### Verification

**Red instrument (observed 2026-10-22):** Normalized replay from the repository root (the historical run used the measured temporary interpreter above):

```bash
uv run python - <<'PY'
import json
from jot_evaluator import _decode_codex
events = [
    {'type':'thread.started','thread_id':'regression'},
    {'type':'turn.started'},
    {'type':'item.completed','item':{'id':'warning','type':'error','message':'non-fatal runtime warning'}},
    {'type':'item.completed','item':{'id':'final','type':'agent_message','text':'{"ok":true}'}},
    {'type':'turn.completed','usage':{}},
]
assert _decode_codex(('\n'.join(map(json.dumps, events))+'\n').encode()) == {'ok':True}
print('PASS: non-fatal warning preserves completed structured result')
PY
```

Actual historical failure (exit **1**, the real decoder engaged; repository prefix sanitized as `<REPO>`, error message unchanged):

```text
Traceback (most recent call last):
  File "<stdin>", line 10, in <module>
  File "<REPO>/jot_evaluator.py", line 228, in _decode_codex
    raise ValueError(
ValueError: Codex did not return a valid structured evaluation from a successfully completed turn. Check `codex login`, your connection, and CLI version; no evaluation was accepted.
```

**Green:** Same command prints the PASS line, exit 0. Record test-specific red→green evidence for the citation protocol before implementation. Then run `uv run python -m unittest discover -s tests` and package asset verification; full suite must pass with only the pre-existing native-Windows skip. Full suite is supporting verification, not the red instrument.

## Phase 2: Observe and document the native isolation boundary

**Goal:** A real saved-transcript-to-HTML boundary probe names failing hops; user-facing isolation guarantees match the evidence.\
**Estimated effort:** S/M; one native evaluator flow, not a new isolation subsystem.

**2026-10-22 amendment:** User explicitly approved one live evaluation per installed evaluator on the saved incident transcript, with usage/credit implications and no retries. Native feasibility found no supported non-billable exact-exec catalog path on 0.163.0. Do not ship an always-unsupported capability script as if it were a verified boundary probe; record the unsupported catalog finding and build the actual approved report-flow probe instead. `app-server skills/list` and `debug prompt-input` do not demonstrate equivalent exec configuration/discovery. Claude Code is not currently on PATH; a missing CLI is a named unverified branch, not permission to install or silently switch providers.

### Tasks
- **2.1:** Use `boundary-probe` for the aspect "a saved transcript becomes a validated HTML report through the selected installed evaluator": source parsing → CLI executable/version → contained native invocation → native/provider completion → local report validation → saved HTML. Add `scripts/probe-evaluator.py` with source, evaluator, output-directory/target parameters, named observations, safe summaries, bounded lifetime/output via the existing runner, and no automatic retries. Reuse actual `evaluate_transcript` and observe real boundaries, not a second invocation implementation. Write outputs only to the opted-in directory; model/usage side effect must require explicit opt-in. Catalog/prompt isolation remains explicitly unobserved metadata, not a passing assertion.
- **2.2:** Prove red using a missing CLI/source without making a provider call, then parent runs one real evaluation per installed evaluator on the saved incident transcript after Phase 1 passes. Record the first failing hop if a live branch fails; do not retry or theorize past it. Keep raw provider diagnostics private. No credential inspection/copying, host configuration changes, or CLI installation is authorized.
- **2.3:** Update [README](<../../README.md>) and [coordinator instructions](<../../jot_assets/agent-workflow.md>) to distinguish fresh sessions/empty project root from skill isolation. Document ID-based raw evidence and legacy support. Record actual tested version/capability limits; do not invent a minimum version. Register the probe and link new evidence from the RCA without rewriting its historical findings.
- **2.4:** Run independent `code-review` and `completion-gate`; address substantive findings and reconcile the progress log.

### Verification

**Red instrument / negative control (observed 2026-10-22):** Normalized equivalent from the repository root; set `TRANSCRIPT` to a locally available saved transcript. The historical command used the absolute temporary interpreter and private Downloads input recorded in the appendix. This equivalent is not a newly observed run:

```bash
PYTHON="$(uv run python -c 'import sys; print(sys.executable)')"
PATH='' "$PYTHON" scripts/probe-evaluator.py "$TRANSCRIPT" --evaluator codex --allow-provider-call
```

Observed probe exit **1**, first failing hop `native_cli`, `native_invocations=0`, with catalog/provider internals explicitly `UNOBSERVED`; no traceback, source text or authentication diagnostics. This is an intentional boundary negative control, not a false success or evidence about unobserved provider internals.

**Acceptance/supporting contracts:** A real provider branch is green only after native completion, local validation, and nonempty Markdown/HTML files are observed through actual code. Normalized repeatable checkout command (set `TRANSCRIPT` to your own available saved input; **fresh explicit consent and normal native filesystem/runtime permissions required**). This command is guidance, **not the literal historically passing command and not claimed run here**:

```bash
uv run python scripts/probe-evaluator.py "$TRANSCRIPT" --evaluator codex --allow-provider-call --output-dir transcripts/verification-local/codex
```

**Historical observation (not a standard-CLI pass under the restricted sandbox):** The initial workspace-only attempt failed at `native_process` before events. A separately user-approved diagnostic captured stderr privately and identified permissions/native state initialization. An exact-command wider-file-access retry was separately approved through the tool; the same real probe with an observational private-stderr wrapper completed native turn → decode → full validation → publication, **64.356s, exit 0**, 107 raw ID citations, 776,736-byte HTML and 66,505-byte Markdown. No application auto-retry/repair was added. The actual wrapper command was `/tmp/jot-triage-standalone.AYWSQP/bin/python /tmp/jot-native-startup-diagnostic.py`; see the progress record for local-only output paths, artifact hashes and privacy-preserving observations, and the appendix below for the exact observer source. The temporary observer is diagnostic instrumentation, not the canonical product implementation; the historical inputs and permissions are not portable checkout fixtures.

**Claude branch:** The same command with `--evaluator claude` and its own output directory failed `native_cli` with zero evaluation invocations because the executable is absent. It remains unverified; do not claim both recovered. Exact exec skill-catalog isolation remains unsupported/unobserved regardless of report-flow success. Supporting full suite (historical temporary runner, normalized checkout command `uv run python -m unittest discover -s tests`) observed **168 discovered, 167 passed, 1 Windows-only skip, exit 0**. Original-machine/0.153.4 compatibility remains unverified.

## Review Log

### 2026-10-22 — Overengineering review
**Mode:** cold subagent (this reviewer did not author the plan; further delegation unavailable)\
**Plan type:** Feature addition / repair to an existing internal CLI\
**Findings:** 0 cut, 0 deferred, 3 kept; substantive acceptance-contract corrections approved by the parent execution agent.
- **Kept:** 1.2/1.3 ID-only v2 plus packaged strict v1 — independent timestamp/quote fields caused the incident; current validator pins version, schema, rubric and digest. No optional substrings, registry, or generalized migration layer is needed.
- **Kept:** 1.1 non-fatal warning support with fatal controls — the actual decoder rejects all error items; accepting warnings must not relax successful-turn/final-object validation or echo arbitrary messages.
- **Kept, narrowed:** 2.1/2.2 native probe — retain negative controls, but gate equivalence before observation and permit an explicitly unsupported result, never a false green. No app-server/exec equivalence or absence of backend requests is assumed.
- **Corrected:** Fitness checks preserve conditional evidence requirements, not a new report-wide quota; source IDs do not prove semantic support.
- Checks 1/2/4/8: no candidates; existing Python/JSON-schema stack and CLI are reused, with no new service, scale layer, runtime dependency, or configurable protocol framework. Checks 3/5/6/7 scrutinized hardest: one derived catalog and two fixed schemas earn their keep; the probe stays bounded and does not become an isolation subsystem.
- Validation recheck: task IDs/phases preserved and progress mirrored; Phase 1 retains its actual decoder red instrument and citation-specific red-before-edit requirement; Phase 2's future command is explicitly predicted and catalog-success gated pending capability evidence. No implementation, provider run, host change, or commit performed by this review.

### 2026-10-22 — Live-verification amendment cold review
- The user approved once-per-installed-evaluator live evaluations. Replace the proposed always-unsupported local catalog script with the real saved-transcript-to-HTML flow probe.
- Reuse actual invocation and validation. Do not fabricate finer native/provider hops than the observer can establish; retain combined observations where appropriate.
- Keep native skill-catalog isolation explicitly unobserved. Missing Claude executable is an unverified branch, not a provider success or permission to install/switch providers.
- Cold reviewer found no blocker to this amendment; scope and former catalog gate are reconciled above.

## References
- [RCA and limitations](<../rca/RCA-2026-10-22-fresh-machine-evaluation-failures.md>)
- [Existing offline incident diagnostic](<../rca/fresh-machine-evidence.py>) — historical broken-behavior replay, not an acceptance gate after repairs; leave historical evidence intact and document this limitation.
- [Provider event semantics](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/exec/src/exec_events.rs#L131-L132>) and [conditional discovery](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/core/src/session/turn_context.rs#L966-L981>).


## 2026-10-23 cloud-review follow-up

The initial four authorized commits (`b31678b`, `34855f1`, `4513f29`, `5f334fb`) are the initial ready [PR #11](<https://github.com/kebaux/kbxJOT/pull/11>) snapshot. Local cubic rounds reported 1, 1, then 0 findings; two findings were declined after runtime checks, without production changes just to appease review. Cloud review reported 12 comments (8 P2, 4 P3). This follow-up addresses nine documentation comments and three code/test comments; the separate review-fix verification section in the progress log records the regression, full-suite, archive and independent cold-review results. The follow-up commit SHA is not known at this documentation handoff and is not needed as a circular self-reference; the progress header identifies committed pre-review baseline `5f334fb`, with current source-content identity and review-fix verification recorded separately by the parent. No new evaluator launch is authorized or performed by this documentation work.

## Appendix: Historical private-stderr observer provenance

The exact passing historical command was:

```text
/tmp/jot-triage-standalone.AYWSQP/bin/python /tmp/jot-native-startup-diagnostic.py
runtime authorization: one-shot exact-command wider-filesystem tool approval
observer SHA-256: ff6ad8a538af96f3fa3aff0983086ce498d257ceb943c53fc67a67dc4910968e
```

The following is an **exact source capture**, read from that temporary file during this follow-up; the UTF-8 content including its final newline has the SHA-256 above. Its author-specific paths are historical metadata, **not reusable commands or available inputs**. The original Downloads source and gitignored output reports are not included and are unavailable to other readers. No raw stderr is published. This is an auditable historical observation shim around the real probe, not a new active CLI, portable fixture, or alternative product implementation. A current checkout can use the normalized command above only with its own input, fresh consent, dependencies and native runtime permissions; it cannot reproduce private original inputs from this appendix.

```python
"""One consented real probe, with private stderr capture and fixed-code classification only."""
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from unittest.mock import patch

root = Path('/Users/kebaux/Development/kbxJOT')
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location('jot_real_probe', root/'scripts/probe-evaluator.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)
real_popen = subprocess.Popen
captured = {'version': bytearray(), 'evaluation': bytearray()}
known_args = set()
class PrivateTee:
    def __init__(self, stream, key):
        self.stream, self.key = stream, key
    def read1(self, size):
        chunk = self.stream.read1(size)
        remaining = 8 * 1024 * 1024 - len(captured[self.key])
        if remaining > 0:
            captured[self.key].extend(chunk[:remaining])
        return chunk
    def __getattr__(self, name):
        return getattr(self.stream, name)
def observe_popen(command, *args, **kwargs):
    process = real_popen(command, *args, **kwargs)
    key = 'version' if '--version' in command else 'evaluation'
    known_args.update(arg for arg in command if arg.startswith('--') and '=' not in arg)
    if process.stderr is not None:
        process.stderr = PrivateTee(process.stderr, key)
    return process
patterns = {
    'unsupported_argument': r'unexpected argument|unrecognized (?:argument|option)',
    'configuration_load_failure': r'error loading config|failed to load config|failed to load configuration',
    'permission_denied': r'permission denied|operation not permitted|read-only file system',
    'log_directory_creation_failure': r'(?:failed|unable|cannot|could not) (?:to )?create (?:the )?(?:log|logs|logging)',
    'database_open_failure': r'unable to open (?:the )?database|cannot open (?:the )?database|failed to (?:open|initialize).{0,40}(?:database|sqlite)',
    'database_write_failure': r'database is (?:locked|readonly|read-only)|attempt to write a readonly database',
    'sandbox_failure': r'sandbox(?:_apply)?.{0,80}(?:fail|denied|permitted)|(?:fail|error).{0,80}sandbox',
    'authentication_failure': r'not logged in|authentication failed|missing.{0,30}(?:api key|credential)|keychain.{0,50}(?:error|fail)',
    'native_state_initialization_failure': r'failed to initialize|failed to create.{0,50}(?:state|session|cache)',
    'network_failure': r'connection refused|connection reset|failed to connect|dns error|network is unreachable',
}
try:
    with patch.object(subprocess, 'Popen', observe_popen):
        code = probe.main([str(Path('/Users/kebaux/Downloads/jot-transcripts/Stanford CS146S How always-on agents work.md')), '--evaluator', 'codex', '--allow-provider-call', '--output-dir', str(root/'transcripts/verification-2026-10-22/codex-diagnostic')])
finally:
    for key, raw in captured.items():
        text = raw.decode('utf-8', errors='replace')
        categories = [name for name, pattern in patterns.items() if re.search(pattern, text, re.I)]
        flagged_arguments = sorted(arg for arg in known_args if 'unexpected argument' in text.lower() and arg in text)
        print(json.dumps({'diagnostic': 'private_stderr_classification', 'process': key, 'stderr_bytes': len(raw), 'categories': categories, 'known_argument_mentions': flagged_arguments}, sort_keys=True), flush=True)
raise SystemExit(code)
```
