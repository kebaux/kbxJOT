# Design Audit — evaluator citation repairs

**Date:** 2026-10-22\
**Method:** Two independent cold implementation reviews, all five code-review phases and APoSD red-flag coverage; parent diff reading and runtime/package verification.\
**Auditor:** Protocol reviewer, probe/documentation reviewer, integrating assistant.\
**Scope:** Thirteen implementation files, working tree versus `12229230188e898c5a0954df392f723baf9b9a53`: nine protocol/validation/packaging/test files and four probe/documentation/test files. Untracked new schemas/scripts/tests were read directly, not omitted from the diff.\
**Excluded:** UI redesign, native CLI internals as a modification target, host credentials/configuration, original-computer compatibility and proof of empty host skill catalogs.\
**Follow-up plan:** [repair plan](<docs/plans/2026-10-22-reliable-evaluator-citations-jxnf.md>); [execution evidence](<docs/progress/2026-10-22-reliable-evaluator-citations-jxnf.md>).

## Summary

The repair reduces knowledge duplication at the critical boundary: model citations identify source entries, and jot alone derives their timing and exact text. Versioned schemas preserve existing audit artifacts rather than silently reinterpreting them. No provider framework, generic migration system, configurable timestamp repair or second evaluator implementation was introduced. Final independent reviews have no outstanding correctness blockers.

## High-priority findings

### H1 — Nonobvious error dispatch — DEFECT, resolved

The [native decoder](<jot_evaluator.py#L194-L249>) used set membership on an unvalidated event discriminator. Cold review reproduced `TypeError` for list/dict event types and silent acceptance of malformed item types followed by a valid final message. This contradicted the bounded malformed-event failure contract.

**Resolution:** Explicit string discriminator checks precede dispatch; no broad TypeError suppression or exhaustive native-item registry. Tests first failed, then passed. Independent reviewer reproduced eight invalid discriminator cases as privacy-safe `event_sequence` failures.

## Secondary findings

### S1 — Compatibility identity shared by test and production — resolved

Legacy fixtures originally loaded the same new packaged schema as production, so future accidental schema drift could make both agree while stranding saved packets. The [legacy tests](<tests/test_jot_agent.py>) now independently pin the canonical semantic identity of the immutable v1 schema. Formatting-only edits remain harmless. Parent also compared it with the real incident request and original git schema.

### S2 — Probe composition scaffolding breadth — optional follow-up

The [probe tests](<tests/test_jot_evaluator_probe.py>) prove reporting, consent, negative controls and privacy but intentionally fake some delegates. A future extension could exercise more fake-native outputs through the real product pipeline. This is not a native boundary proof and was not required to accept the probe: the parent actually ran the real evaluator path and observed native completion, full local validation and newly published HTML. Revisit if product hook signatures change.

## What's working

- [Source catalog and validator](<jot_agent.py#L170-L282>) own ID resolution and evidence/range authority together. A separate validated deep-copy view prevents raw response mutation without exposing a new public resolver workflow.
- [Versioned schema assets](<jot_assets/evaluation-response.schema.json>) and [immutable v1 schema](<jot_assets/evaluation-response-v1.schema.json>) are explicit protocol boundaries, not speculative compatibility knobs. New response citations cannot independently pair a quote with another entry's timestamp.
- Fixed stage diagnostics and capped evidence aggregation preserve useful rejection scope without exposing source/model values. Nonfatal native warnings cannot substitute for required thread/turn/final/completion frames or rescue a fatal event.
- The [development probe](<scripts/probe-evaluator.py>) observes actual delegates and reuses the product's bounded runner, invocation and validator. Its wrappers are deliberate diagnostic instrumentation, not a second production pipeline. Missing observations cannot produce green success.
- [Packaging](<pyproject.toml>) remains an explicit manifest. Scripts are included in sdist because its tests import them; the wheel remains runtime-only. Actual archives and an outside-checkout installed wheel were exercised.
- [README](<README.md>) and [coordinator contract](<jot_assets/agent-workflow.md>) distinguish fresh-session/project isolation from home skill discovery. No startup warning absence, token count or adjacent catalog RPC is treated as an isolation guarantee.

## Suggested refactoring order

No additional production refactor is justified by this slice. Retain cohesive source authority and strict version selection. Extend diagnostic composition tests only when a concrete boundary/signature change makes them useful; do not add a generic observer/plugin API to avoid local private development hooks.

## Verification

- Parent full suite: 168 discovered, 167 passed, one native-Windows-only skip; exit 0, 11.346s. Extracted sdist and outside-checkout installed wheel independently verified by executor and archive bytes rechecked by parent/reviewer.
- Final protocol reviewer snapshot SHA-256: `58c7ab5422bf2606ab1dda53a15166fd90779a48fa5a0d84e27db069d3953977`; no remaining blockers.
- Real native missing-CLI control: first failed hop `native_cli`, zero evaluation invocations, expected nonzero exit.
- Real Codex 0.163.0: startup initially failed with no events under workspace-only file access. A separately consented private diagnostic classified permission/native-state initialization errors. Exact-command wider-file-access retry was explicitly approved and completed one real turn, validation and publication in 64.356s, exit 0; 107 raw ID citations passed independent revalidation without response mutation. No application retry or weaker validation was added.
- Claude's executable was absent: live branch stopped at CLI lookup, zero evaluation invocations. Original-machine compatibility, host catalog/prompt isolation and factual/semantic truth remain unverified.

## Audit checklist

- [x] Full scoped diffs and untracked implementation files read; cross-module callers traced.
- [x] All 17 APoSD flags considered, including speculative parameters/premature extraction; no unnecessary abstraction introduced.
- [x] Depth assessed; source identity, protocol versions, publication and native event knowledge traced to their owners.
- [x] Deliberate v1/v2 duplication and private diagnostic hooks evaluated against recorded rationale rather than relitigated without evidence.
- [x] Framework/native behavior verified with actual tests or tagged upstream source; archives and installed runtime provenance checked.
- [x] Present defect H1 reproduced, prioritized, fixed and independently reverified before live acceptance.
- [x] Error paths, privacy, comments/names, raw nonmutation and all-or-nothing publication checked.
- [x] Findings persisted; no unrecorded blocker, commit, host-auth change or hard-isolation claim.
