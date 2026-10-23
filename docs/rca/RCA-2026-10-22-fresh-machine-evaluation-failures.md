# RCA: Two independent evaluation failures on a fresh computer

**Date:** 2026-10-22\
**Last updated:** 2026-10-23 (documentation/provenance follow-up)\
**Severity:** High — neither attempted evaluator produced the requested watch page; source artifacts survived.\
**Historical triage status (checkout `1222923`):** Causes identified; no product fixes had been implemented at that point. Original full Codex stdout unavailable. Later implementation/review status is in the linked execution record below.\
**Mode:** Trace + forensic + environment comparison\
**Checkout examined:** `1222923` (2026-10-16).

> **Implementation follow-up:** The findings and verification record below describe the original pre-fix checkout. See the [repair plan](<../plans/2026-10-22-reliable-evaluator-citations-jxnf.md>) and [execution evidence](<../progress/2026-10-22-reliable-evaluator-citations-jxnf.md>) for subsequent changes and live-verification outcomes. The original [offline diagnostic](<fresh-machine-evidence.py>) deliberately asserts the old broken behavior; it is historical evidence, not the repaired-code acceptance gate.

Source links below are checkout-relative locators; historical source line ranges and behavior refer to examined revision `1222923`, not a claim that the repaired files still implement that behavior.

## Summary

This was not one installation failure. Caption capture succeeded twice. Claude returned a structurally valid assessment with **one wrong quote/timestamp association out of 43 citations**; jot correctly refused publication. Its citation protocol still asks the model to reproduce two independently writable fields, so copying guidance cannot guarantee their association. The Codex failure is a different integration defect: jot treats a **documented non-fatal warning item as a fatal turn failure**, then replaces the actual reason with login/connection/version advice. Host skill discovery can trigger that warning despite jot's restrictions. Version differences plausibly explain why it escaped testing: the verified Codex 0.162.1 no longer emits this particular shortened-description warning, while the reported 0.153.4 does. Neither upgrading nor loosening evidence validation is a complete repair.

## Evidence and confidence

The incident inputs below are **local-only investigator evidence**, not included in this repository and unavailable to other readers in a clean checkout. These are labeled path/hash metadata, not download links. No source transcripts, raw reports, credentials, or other original inputs are being committed.

```text
incident narrative: /Users/kebaux/Downloads/message.txt
narrative SHA-256: not recorded in the original forensic result
artifact root: /Users/kebaux/Downloads/jot-transcripts/
Stanford CS146S How always-on agents work.md
  SHA-256: 4c2f0224bc5a6c2ba5318337209baa961f982f48bb8d3be10522226e8d4d381c
Stanford CS146S How always-on agents work.request.json
  SHA-256: 8d1512d4ed2a2c6758d656bb8a8af52f72a6c1c0bca60e571ea89e5e749d9047
Stanford CS146S How always-on agents work.request.response.json
  SHA-256: a8da3593350fdc10fd9aa5a3b7b9f6e608ee9354546ba5033f6c3ff309e81bd1
Stanford CS146S How always-on agents work (1).md
  SHA-256: c9187a916ba19fb457f8c02cabd78bdc7d7f272bf7a5b31f10713f1ae671cf17
Stanford CS146S How always-on agents work (1).request.json
  SHA-256: ede7de7653a6ed192dd5ca31a6e84e55b9cf09dfbdb0537f948cdb3988ca5192
```

- [Offline diagnostic](<fresh-machine-evidence.py>) and [saved machine-readable results, including artifact SHA-256 hashes](<2026-10-22-fresh-machine-evidence.json>) are tracked provenance. The unchanged diagnostic makes no provider calls or original-artifact changes and intentionally asserts the **old broken behavior**, including the old schema and decoder rejection. It is **not a repaired-code acceptance gate** and is not runnable as-is from a clean checkout. An investigator needs the five original hash-matching artifacts at the hard-coded Downloads directory, project dependencies, repository-root working directory, and the historical `1222923` implementation/schema to replay its original assertions. The narrative is additional evidence for the quoted reconstructed Codex stream, not a file read by the diagnostic. Use the saved result when those private inputs/environment are unavailable; do not fabricate them or run this diagnostic as a current acceptance test.
- **Confirmed directly:** source/request equality, both request digests, packaged schema/rubric equality, identical transcript speech, 1,357 caption lines at 1,351 distinct timestamps, duration 2,717 seconds, schema-valid Claude response, exactly one bad citation, full local validation after one in-memory timestamp substitution, deterministic decoder rejection caused solely by adding the warning item.
- **Confirmed from upstream tagged source:** warning-item semantics, conditional host-discovery bypass, and removal of this specific warning by 0.162.1.
- **Reported, not independently recaptured:** original Codex 0.153.4 runtime, 79-second evaluation, return code 0 and 13,386 input tokens from the trivial reproduction, host skill/plugin counts. The provided directory has five artifacts and no original Codex event stream or response. Its absence is consistent with decoder failure, not proof of that failure by itself.

## Timeline

| Time | Event | Provenance |
|---|---|---|
| 2026-10-14 | Citation lookup/copy guidance introduced in `ea82b38`; timestamp and quote remain independently writable. | Git blame of [citation generation](<../../jot_agent.py#L339-L353>). |
| 2026-10-15 | Codex integration and unconditional error-item rejection introduced in `3df112c`. | Git blame of [decoder](<../../jot_evaluator.py#L194-L231>). |
| 2026-10-21 03:27 UTC (Oct 20, 23:27 EDT) | First saved caption capture; Claude assessment later rejected. | Local-only first transcript metadata, lines 5–10 (inventory above); run order from incident narrative. |
| 2026-10-21 03:31 UTC (Oct 20, 23:31 EDT) | Second capture; Codex evaluation later rejected. | Local-only second transcript metadata, lines 5–10 (inventory above); run order from narrative. |
| Later, exact time unknown | Reporter reproduced Codex warning rejection using a trivial boolean schema. | Quoted event stream in the local-only incident narrative, lines 64–104 (inventory above). |
| 2026-10-22 EDT | This investigation reproduced local failures, checked tagged upstream source, and ran the existing suite. | Diagnostic results and verification below. |

Capture times are not evaluator start/end times. The 45-second Claude and 79-second Codex durations are reported, not independently timed here. No successful baseline from the other computer was supplied.

## Failure A — Claude: valid quote attached to the next caption's timestamp

### Exact symptom

```text
takeaways[5]: quote is not an exact source span at timestamp 1909: 'a point where it needs to summarize and'.
```

The source is unambiguous:

```text
[31:47] a point where it needs to summarize and
[31:49] all compression is lossy. So you have to
```

The local-only first transcript, lines 971–972, and saved Claude response, lines 117–118, supplied this observation (inventory above; unavailable to other readers). The quote occurs in exactly one timestamp bucket: **1907**, not 1909.

### Cause-first chain / grounded whys

1. The [response contract](<../../jot_assets/evaluation-response.schema.json#L67-L75>) lets the model supply a timestamp and quote independently; JSON shape constraints do not bind the pair to a source entry.
2. Jot supplies correct candidate pairs and [explicit copying instructions](<../../jot_assets/evaluator-instructions.md#L9-L18>), but these are model guidance rather than a construction guarantee.
3. Claude returns an exact quote paired with the following caption's timestamp. We can observe the wrong pair; we cannot know its internal reasoning or whether it copied from lookup versus the original transcript.
4. The [local evidence validator](<../../jot_agent.py#L200-L215>) looks only in source spans at the supplied timestamp and raises on the first invalid citation.
5. [Publication validates before rendering/writing](<../../jot_agent.py#L292-L305>), so the entire report is withheld. The [response is saved first](<../../jot_agent.py#L355-L366>), explaining why a response survives without evaluation HTML.

**Root cause of the invalid association:** a redundant citation representation whose cross-field consistency depends on fallible model copying. **Reason no partial report appeared:** deliberate all-or-nothing publication, not a broken renderer. The validator did catch the problem; the prompt and schema did not prevent it.

### One-variable falsification test

Hypothesis: this one timestamp, rather than malformed captions, schema drift, packet identity, or another invalid citation, is sufficient to explain the saved response rejection.

- Original saved request + response: full validator reproduces the exact exception.
- Independently scan all evidence fields: **42 valid / 1 invalid**.
- Deep-copy the response and change only `takeaways[5].evidence[2].timestamp` from 1909 to 1907: **full validation passes**.
- No artifact was rewritten and no corrected report was published. Passing local validation does not establish factual accuracy or complete semantic support for every narrative claim.

This failure is not shown to be fresh-machine-specific. It can occur on any machine when the model produces an invalid pair. No evidence establishes a model/version/environment change as the cause of Claude's choice.

## Failure B — Codex: successful turn rejected for a non-fatal item

### Exact symptom

```text
Codex did not return a valid structured evaluation from a successfully completed turn. Check `codex login`, your connection, and CLI version; no evaluation was accepted.
```

The reporter's trivial reproduction says the process exited 0 and emitted, in order: `thread.started`, `turn.started`, an `item.completed` with `item.type="error"` carrying the shortened-skill-description warning, a valid `agent_message` containing `{"ok":true}`, and `turn.completed`.

### Cause-first chain / grounded whys

1. Codex distinguishes a non-fatal **item** error from a fatal **stream/turn** error. The [0.153.4 event definitions](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/exec/src/exec_events.rs#L131-L132>) explicitly call the item non-fatal. [Top-level error](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/exec/src/exec_events.rs#L22-L36>) is a separate unrecoverable event.
2. Its [upstream regression test](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/exec/src/event_processor_with_jsonl_output_tests.rs#L65-L90>) maps a runtime warning to an error item while leaving status `Running`. This is intended protocol behavior, not evidence of failed authentication.
3. Jot's [decoder:210–213](<../../jot_evaluator.py#L210-L213>) instead treats every `item.type == "error"` as fatal. It raises immediately and never reads the later final message/completion.
4. The [exception handler:227–231](<../../jot_evaluator.py#L227-L231>) discards the internal reason and substitutes generic login/connection/version advice. That diagnostic directs attention to the wrong layer.
5. Since invocation never returns a decoded object, [response persistence and publication](<../../jot_agent.py#L350-L366>) are never reached. This explains a preserved request without a Codex response or HTML.

**Root cause:** jot's native-event adapter implements the wrong failure semantics. Successful process exit plus a completed turn cannot rescue it because it rejects earlier in the stream. Auth readiness checks cannot detect this parser mismatch.

### One-variable falsification test

Hypothesis: the quoted warning alone is sufficient to make the local decoder reject an otherwise successful response.

- Reconstruct the quoted event sequence with a valid final boolean object; without the warning, decoding returns `{"ok":true}`.
- Add only the warning item: decoding reproduces the exact generic exception.
- Controls containing `turn.failed` or top-level `error` are also rejected.

This establishes the decoder defect. It does **not** prove the missing original 79-second Codex evaluation had otherwise publishable evidence. The reporter's trivial result is not the full evaluation result; after repairing decoding, independent schema/evidence failures could still emerge.

## Why host skills and CLI version matter

### The isolation setting is weaker than its name suggests

Jot [uses an empty working directory but inherits the environment except session identifiers](<../../jot_evaluator.py#L259-L307>), retaining home/auth locations. Empty project context is not an empty host skill catalog.

In upstream 0.153.4:

- [`--ignore-user-config` leaves an empty user-config layer](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/config/src/loader/mod.rs#L526-L541>), rather than removing the user's home location.
- [Host skill roots use that layer's source/location](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/ext/skills/src/host_roots.rs#L80-L114>) to discover native skills and home agent skills, independently of the ignored TOML contents.
- The [app server registers a host skill provider](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/app-server/src/extensions.rs#L114-L124>); the [skills extension then requires host discovery](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/ext/skills/src/extension.rs#L325-L331>).
- The [skip conditional](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/core/src/session/turn_context.rs#L966-L981>) skips discovery only when the flag is true **and no extension requires discovery**. The flag is therefore not a hard isolation barrier.

This explains how a home skill catalog can survive jot's intended suppression. It does not establish that every skill body was injected, plugins were active, credentials were exposed, or the host conversation was reused. In fact [plugin loading has its own disabled-feature short circuit](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/core-plugins/src/manager.rs#L761-L764>). Counts of installed plugins and a high input-token count do not prove plugin activation. The precise catalog used on the original machine remains unobserved here.

### The version difference is a plausible trigger difference, not the fundamental decoder cause

The [README records verification against 0.162.1](<../../README.md#L9-L13>); the incident reports 0.153.4. Source comparison matters:

- [0.153.4 skill rendering](<https://github.com/openai/codex/blob/rust-v0.153.4/codex-rs/ext/skills/src/render.rs#L93-L114>) warns when average description truncation crosses its threshold.
- [0.162.1 rendering](<https://github.com/openai/codex/blob/rust-v0.162.1/codex-rs/ext/skills/src/render.rs#L94-L113>) no longer emits that truncation-only warning; omitted skills can still produce a warning.
- [0.162.1 still tests runtime warnings as non-fatal error items](<https://github.com/openai/codex/blob/rust-v0.162.1/codex-rs/exec/src/event_processor_with_jsonl_output_tests.rs#L66-L91>).

Consequently, an upgrade may remove this particular trigger while leaving the adapter defect and host skill discovery intact. A newer-version success would not prove those defects fixed. The current investigation machine has Codex 0.163.0, not the reported 0.153.4; no paid provider calls or CLI upgrades were performed.

## Why the tests were green

- [Citation tests](<../../tests/test_jot_agent.py#L229-L243>) correctly require moved/fabricated quotes to fail. This incident confirms that safety invariant, while exposing a separate generation-reliability weakness.
- [Codex test:583](<../../tests/test_jot_evaluator.py#L574-L589>) explicitly lists an error item inside an otherwise successful turn as invalid. The test encodes the integration mistake.
- The [fake Codex executable](<../../tests/test_jot_evaluator.py#L409-L454>) checks command-line arguments and returns a hand-authored successful sequence. It does not exercise the installed Codex skill loader or runtime warning behavior. Passing flag assertions proves flag construction, not effective isolation.
- [Setup readiness](<../../jot_config.py#L129-L145>) checks executable presence and login status only, not version compatibility or native-event decoding. That matches the current setup description; readiness is not an evaluator contract test.

## Repair recommendations — not yet implemented at historical triage

1. **Repair Codex event interpretation without weakening publication.** In [the adapter](<../../jot_evaluator.py#L194-L231>), distinguish non-fatal item errors from `turn.failed`, top-level errors, nonzero process status, malformed events, missing completion, and invalid final JSON. Still require the complete local report validator. Replace the test that mandates the false rejection with a realistic warning-plus-success case and retain fatal-event controls.
2. **Give citations a single authoritative source identity.** Change the generation protocol in [schema](<../../jot_assets/evaluation-response.schema.json#L67-L75>), [lookup creation](<../../jot_agent.py#L343-L353>), and [instructions](<../../jot_assets/evaluator-instructions.md#L9-L18>) so the model references a stable entry ID; derive timestamps locally. If shorter quotes remain supported, validate the exact substring against that referenced entry. Preserve the source authority, unknown-ID rejection, repeated/equal-timestamp cases, and range checks. This removes the independent timestamp-copying failure, not every possible citation/semantic error. Keep original output auditable and handle protocol-version compatibility explicitly.
3. **Do not silently repair evidence or publish partial invalid reports.** Neighbor-timestamp reassignment changes provenance and is ambiguous for repeated speech. Retrying changes cost and the documented workflow. Both are policy changes, not substitutes for a better citation representation; neither is required for this diagnosis.
4. **Report the actual rejection stage safely.** Expose bounded stage/reason codes and counts, separating process failure, event decoding, JSON/schema, and citation validation. Collect all citation failures to show scope. Do not print arbitrary provider warning text: it can contain source text, paths, or authentication details. Preserve privacy rather than guessing what substrings are sensitive.
5. **Resolve the actual isolation contract.** Fresh session, empty project root, ignored config, disabled tools, and no host skill discovery are different properties. Either support and demonstrate real skill-catalog isolation with native auth preserved, or document the remaining host discovery accurately in [the coordinator contract](<../../jot_assets/agent-workflow.md#L16-L18>). Merely setting another unverified flag or observing no warning is not proof. A temporary `CODEX_HOME` alone may still leave home-based agent skills and auth handling unresolved.
6. **Make supported CLI compatibility explicit.** Record and check a tested capability/version policy rather than treating a successful login as proof of evaluation compatibility. A minimum version can reduce known triggers, but cannot replace correct event semantics.

## Prevention and unobserved boundaries

User-visible aspect: **an authenticated user supplies a video and receives a validated HTML watch page**.

| Hop | Existing evidence/coverage | Blind spot requiring real observation |
|---|---|---|
| URL → captions → saved source/request | Fixture tests plus two real saved captures | Future capture availability is not rechecked here. |
| Jot process → installed native CLI/config/skill catalog | Fixture argument checks; upstream source; reporter's trivial reproduction | Exact failing-machine CLI behavior and effective catalog need a real runtime probe. |
| Native CLI → provider → native final message/events | Reporter quotes a trivial completed request | Original full Codex stdout absent; no new provider request made. |
| Native events → jot decoder → full evidence validation | Offline one-variable replays and direct Claude artifact validation | Missing original Codex report cannot be reconstructed. |
| Validated report → saved Markdown/HTML | Existing renderer/publication tests | No real repaired provider evaluation/published HTML was produced in this triage. |

A native-provider boundary probe is justified (multiple process/provider boundaries, mocks replace the failing implementation, and host-dependent costly failures). It should record CLI version, effective catalog/canary evidence, event types, completion status, decoding stage, and local validation outcome; target the original machine/version and compare a controlled skill-catalog environment. Warning absence and lower token counts alone are not success criteria. This is a handoff, not a claim that such a probe was built or run. Triage does not authorize silently making billable evaluator calls or changing host authentication/configuration.

After implementation, closure requires: warning-plus-success accepted while fatal controls remain red; citation-ID mismatch impossible or rejected deterministically; demonstrable isolation (or an accurately narrowed contract); and the original video producing validated HTML with **both** evaluators on the target environment. A green fixture suite alone is insufficient.

## Verification record and limitations

Historical commands ran with `/tmp/jot-triage-standalone.AYWSQP/bin/python` (ephemeral measured runner, not a mandatory dependency). Normalized equivalents below require a dependency-installed checkout; the diagnostic additionally requires the historical implementation and private investigator inputs described above. These commands are not claimed newly run:

```bash
uv run python docs/rca/fresh-machine-evidence.py
uv run python -m unittest discover -s tests -v
```

**142 discovered, 141 passed, 1 native-Windows-only skip; exit 0, 10.076 seconds.** This is unchanged-product-code behavior, including the test that enforces the warning-rejection bug. Dependencies were freshly resolved from declared ranges, not recreated from the incident machine or the lockfile. Runtime: standalone CPython 3.12.15 in a disposable temporary venv.

Earlier verification attempts failed for investigation-environment reasons: the system Python is 3.9.6 with missing dependencies; the GUI-bundled Python rejected newly installed native modules on macOS Team-ID/library-validation grounds; an initial standalone run depended on `PYTHONPATH`, which the containment fixture deliberately clears, causing one child-import/PID test failure. Giving the standalone venv its own dependency path resolved the latter without changing product/test code. These are not additional causes of the reported incident.

The [offline diagnostic](<fresh-machine-evidence.py>) exercises the actual parser/validator/decoder, not stubbed replacements. Its Codex stream is explicitly reconstructed from the report. The single timestamp counterfactual stays in memory. No report was published, original evidence modified, provider authentication read, or live evaluator invoked.

## Open questions

1. **Was the original full Codex response otherwise valid?** Unknown; need the original stdout or a consented instrumented rerun. This determines whether decoder repair alone restores that run.
2. **Which exact host skills and model were used?** Unknown; need original effective skill catalog/config diagnostics and CLI/model metadata, without exposing credentials. Directory counts and token totals are insufficient.
3. **Would the newer CLI avoid this run's symptom?** The source supports removal of the exact warning, but no same-environment comparison was performed. Even a successful upgrade would not establish hard isolation or correct warning handling.
4. **Did the other computer work reliably?** No known-good artifacts/environment were supplied, so this is not established as a regression caused by machine migration.
5. **Why did Claude choose that wrong pair internally?** Not observable. The invalid pair and the protocol weakness are established; any explanation of its reasoning would be speculation.
