# Progress: Reliable evaluator citations and native warning handling

**Plan:** [implementation plan](<docs/plans/2026-10-22-reliable-evaluator-citations-jxnf.md>)\
**Started:** 2026-10-22\
**Last updated:** 2026-10-22\
**Status:** Complete — implementation, reviews, package/local tests and current-machine Codex report path verified; Claude/original-machine/host-catalog limits remain explicit below.
<!-- phase: 2 · verified-at: 1222923 + uncommitted implementation; protocol snapshot 58c7ab5422bf2606ab1dda53a15166fd90779a48fa5a0d84e27db069d3953977 -->

## Phase 1: Repair the local generation-to-publication contract

**Status:** Complete — independent cold review accepted after the malformed-discriminator correction and final archive checks. This is completion of the local contract repair, not a claim that every installed/native-provider branch succeeded.

**Class / revision:** Standard; `main` at `1222923`, zero commits since plan watermark. Verification includes uncommitted Phase-1 changes and concurrently implemented Phase-2 work. No commits, model calls, or host configuration/authentication changes by the Phase-1 executor.

- [x] 1.1 Codex warning/event diagnostics and regression controls.
- [x] 1.2 Versioned ID citations, legacy schema, packaging and instructions.
- [x] 1.3 Citation protocol/evidence/publication regressions.

### Implementation / review record
- New requests declare version 2 and ID-only citations. A deterministic source-derived physical-line catalog preserves exact whitespace, duplicate timestamps/quotes and untimed prelude. Publication reconstructs authority and resolves a deep-copied render view; saved raw responses retain IDs, without timestamp correction, retries or partial reports.
- Version 1 uses the byte-identical historical schema with trusted rubric/schema/digest checks. Original quote/timestamp failure tests remain meaningful v1 tests. A canonical semantic schema hash independently pins immutable persisted v1 compatibility, allowing formatting-only changes.
- Completed native warning items are accepted after the thread starts, including before the turn starts; ordinary final messages still require the turn. Fatal events, incomplete/misframed streams, malformed/duplicate JSON, invalid UTF-8, invalid final objects and nonzero process exits remain rejected. Error reporting uses fixed stage codes; schema/evidence diagnostics omit private values and aggregate evidence failures (first 20 safe locations, total count retained).
- Cold reviewer arranged by parent found malformed event types could escape as TypeError and malformed item types could survive a later valid final. Explicit string-type guards and regressions address both; focused/full verification below is after that fix. Reviewer also requested the v1 schema semantic pin, now added. Parent owns final cold-review acceptance.
- Parent-authorized packaging reconciliation: include `scripts` in sdist only, since the Phase-2 probe test imports its script. Wheel remains runtime-only. No probe/coordinator/README edits by this executor.

### Verification evidence — 2026-10-22
- Phase-start snapshot retained at `/var/folders/rg/l2cylb1j32zfqzr4gwnh9l9m0000gn/T/jot-phase1-before.ik4uq8og`; captures tracked and non-ignored untracked files, preserving modes/symlinks and prior RCA/plan work.
- Baseline warning-acceptance reproduction: actual decoder raises generic ValueError, exit 1 (full command/output in plan). Reconfirmed directly before product edits.
- Baseline full suite collected by parent through `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests`: 142 run, 1 skipped, OK; exit 0, 10.501 seconds. This is unchanged-code supporting evidence, not repair verification.
- Citation red → green, same command: `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests -p test_jot_citation_v2.py -k preparation`. Before implementation: `Ran 1 test in 0.008s`, `FAILED (failures=1)`, `AssertionError: 1 != 2`, exit 1. After: `Ran 1 test in 0.008s`, `OK`, exit 0. The broader preimplementation citation run also rejected `source_id` as an additional property under the old schema.
- Warning red → green, same command: `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests -p test_jot_evaluator.py -k warning_items`. Before: `Ran 1 test in 0.128s`, `FAILED (errors=1)` with the old generic decoder rejection, exit 1. After: `Ran 1 test in 0.348s`, `OK`, exit 0 (includes startup/runtime positions, varied arbitrary messages and fatal controls).
- Review-fix red: `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests -p test_jot_evaluator.py -k malformed_event_and_item`: `Ran 1 test in 0.275s`, `FAILED (failures=4, errors=2)`, exit 1. Lists/dicts caused TypeError; four invalid item types were accepted. After explicit guards, `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests -p test_jot_evaluator.py`: `Ran 30 tests in 4.746s`, `OK (skipped=1)`, exit 0.
- **Final working-tree full suite:** `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests`: `Ran 168 tests in 11.358s`, `OK (skipped=1)`, exit **0**. Only native Windows Job Object regression skipped. Phase-2 tests are included in this supporting run.
- Packaging tools installed only in disposable runner: `/tmp/jot-triage-standalone.AYWSQP/bin/python -m pip install --disable-pip-version-check build hatchling`, exit 0. Build: `/tmp/jot-triage-standalone.AYWSQP/bin/python -m build --no-isolation --outdir /tmp/jot-phase1-packages-jxnf`, exit 0, `Successfully built jot-0.1.0.tar.gz and jot-0.1.0-py3-none-any.whl`.
- Archive assertions (stdlib zipfile/tarfile, exit 0): both artifacts contain exact current agent/evaluator modules, current+legacy schemas, evaluator instructions and rubric; legacy bytes equal `git show HEAD:jot_assets/evaluation-response.schema.json`. Sdist additionally contains exact `scripts/probe-evaluator.py`, `tests/test_jot_evaluator_probe.py` and `tests/test_jot_citation_v2.py`; wheel has no scripts.
- **Extracted final sdist suite:** run `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests` with working directory `/var/folders/rg/l2cylb1j32zfqzr4gwnh9l9m0000gn/T/jot-sdist-final.ijggdm47/jot-0.1.0`: `Ran 168 tests in 11.238s`, `OK (skipped=1)`, exit **0**.
- Final wheel installed with `pip install --no-deps --no-compile --target` into `/var/folders/rg/l2cylb1j32zfqzr4gwnh9l9m0000gn/T/jot-wheel-final-site.j_nk0_vd`; smoke ran outside checkout in `/var/folders/rg/l2cylb1j32zfqzr4gwnh9l9m0000gn/T/jot-wheel-final-check.r6kyj_yd`. Asserted both imported module paths lie in isolated target. Actual v1 and v2 publication created Markdown+HTML with seek links and unchanged raw response files; malformed event types rejected with bounded sequence code. Three PASS lines, exit 0.
- Read the actual tracked diff and added schema/tests; `git diff --check` exit 0. Final full-file-universe snapshot retained at `/var/folders/rg/l2cylb1j32zfqzr4gwnh9l9m0000gn/T/jot-phase1-after.ii4zflja`; scoped nine-file Phase-1 review delta at `/var/folders/rg/l2cylb1j32zfqzr4gwnh9l9m0000gn/T/jot-phase1-after.ii4zflja.phase1.diff` excludes concurrent Phase-2 edits. No Standard-phase steps skipped; independent final review remains parent-owned.
- **Parent-supplied independent incident evidence:** packaged legacy schema equals saved incident schema and HEAD schema; original bad response still rejected with `failures=1` without quote echo. In-memory timestamp1907 counterfactual validates; original1909 remains untouched, no report published. Source catalog has 1,357 IDs (0–1,356); unique incident quote ID955 resolves1907.

### Limitations / handoff
- No Phase-1 executor live calls. Parent reports its separately authorized Codex0.163.0 attempt failed at native process exit1 with stdout0 in0.718s and zero thread/turn events; decoder/validator were not reached. Cause remains unknown because stderr is discarded by design. No retry was made by this executor. This offline verification does not claim provider recovery or native catalog isolation.
- Phase-1 product/test files frozen pending parent acceptance; no final completion watermark updated. Parent handles remaining independent review and any authorized live diagnostics, then Phase-2 reconciliation.

## Phase 2: Observe and document the native isolation boundary

**Status:** Complete — native Codex report path passed after explicitly approved wider-file-access verification; Claude branch could not run because its executable is absent. Exact catalog isolation remains unsupported/unobserved.

- [x] 2.1 Real saved-transcript-to-HTML probe reusing actual product delegates, with mandatory live-call opt-in, no retry, safe named-hop summaries, bounded process/output containment and explicit unobserved internals/catalog.
- [x] 2.2 Real missing-CLI negative control and native startup failure identified; exact-command, explicitly approved wider-access diagnostic completed a real Codex turn, full validation and publication. Claude remains an explicitly unavailable branch.
- [x] 2.3 README/coordinator guarantees narrowed; raw v2 response+request audit and legacy compatibility documented.
- [x] 2.4 Independent four-file cold review accepted; parent full regression and archive verification passed. Live outcome remains separate below.

### Verification and review evidence — 2026-10-22
- Native feasibility: Codex 0.163.0 has no established exact-exec nonbillable catalog interface. Standalone app-server catalog RPC and debug prompt generation have non-equivalent configuration/lifecycle; saved-login startup may itself contact a backend. No alternate RPC was run. Plan amended after user approved one real saved-transcript evaluation per installed evaluator, rather than shipping an always-unsupported pseudo-probe.
- [Probe](<scripts/probe-evaluator.py>) and [five scaffolding tests](<tests/test_jot_evaluator_probe.py>) exercise consent guard, actual missing executable lookup, privacy-safe malformed-event summaries, artifact setup failure, and successful/failing observed delegate paths. Focused suite: 5 tests passed, exit 0. Fake provider tests are not native/provider evidence.
- Parent repeated the actual negative control with `PATH=''` and absolute standalone Python running `scripts/probe-evaluator.py` on the saved source: final `native_cli` FAIL, `native_invocations=0`, probe exit 1, explicitly asserted by shell. No model call.
- Actual Claude branch: same probe, evaluator `claude`, explicit output directory under `transcripts/verification-2026-10-22/claude`: `native_cli` FAIL, `native_invocations=0`, exit 1. Claude executable absent from PATH and common local/npm locations. No install, provider substitution, or Claude evaluation performed.
- First approved Codex attempt: version 0.163.0 preflight PASS; source request PASS (72,159 bytes); native process exit 1, stdout 0 bytes, zero thread/turn/agent events, 0.718s. Decoder/validator never reached. No automatic retry.
- User then explicitly approved one diagnostic attempt. A temporary parent-only stderr observer delegated to the exact real subprocess and emitted only fixed pattern-classification codes, never raw diagnostics. That attempt again exited 1 before events (0.322s): evaluation stderr 199 bytes classified `permission_denied` plus `native_state_initialization_failure`; version stderr 104 bytes classified `permission_denied`. This establishes a runtime permission/startup boundary, not a model/schema/evidence failure; no exact private path was exposed or inferred.
- Parent requested one-shot wider filesystem access for the **exact same diagnostic command** through the tool's explicit approval mechanism. The approved retry completed successfully in **64.356s**, exit **0**, with native stderr **0 bytes** (version and evaluation). Actual native observations: one thread start, one turn start, one completed agent message, one turn completion; zero fatal errors/failed turns/warning items/invalid JSON; stdout 10,231 bytes. Native decode, full local validation and publication all passed, with exactly one evaluation invocation. Wider file access was the only intentional runtime-policy change; this supports the earlier failure being this session's filesystem restriction, not a response-schema/evidence failure. This is permission-controlled environment verification, not weakened publication or an automatic application retry.
- Independent Phase-2 cold reviewer read final four-file diff plus actual product boundaries: no substantive blockers; 5 focused tests passed. Independently reproduced a missing-source `source_request` failure before any evaluation. Optional suggestion to broaden fake-native/product composition tests deferred: current product regression suite plus real parent run cover the intended closure; no weaker trust boundary added.
- Independent Phase-1 final review: 0 remaining critical/warning/suggestion findings after explicit discriminator guard and immutable legacy schema pin. Reviewer independently reproduced eight malformed discriminator cases as safe `event_sequence` failures; 90 focused tests passed with 1 native-Windows skip. Final nine-file snapshot SHA-256 `58c7ab5422bf2606ab1dda53a15166fd90779a48fa5a0d84e27db069d3953977`.
- Parent independently reran full final working tree: `/tmp/jot-triage-standalone.AYWSQP/bin/python -m unittest discover -s tests` → **168 discovered, 167 passed, 1 native-Windows skip**, 11.346s, exit **0**.
- Parent independently checked real final wheel/sdist bytes against working-tree modules, both schemas, instructions, source probe and tests; original v1 schema equals the HEAD persisted protocol; `git diff HEAD --check` passed. Reviewer also inspected exact archive contents, not just build summaries.

### Live artifacts and remaining limits

- [Generated Codex HTML](<transcripts/verification-2026-10-22/codex-diagnostic/Stanford CS146S How always-on agents work.evaluation.html>) — 776,736 bytes; SHA-256 `103d73cd667922fe7c56956bace530bb9ccb2331ccb28a3bffc0f9dc22c75ef7`.
- [Markdown companion](<transcripts/verification-2026-10-22/codex-diagnostic/Stanford CS146S How always-on agents work.evaluation.md>) — 66,505 bytes, original transcript preserved as the unchanged suffix.
- [Actual v2 request](<transcripts/verification-2026-10-22/codex-diagnostic/Stanford CS146S How always-on agents work (1).request.json>) and [raw model response](<transcripts/verification-2026-10-22/codex-diagnostic/Stanford CS146S How always-on agents work (1).request.response.json>) — **107 ID-only citations**, independent parent revalidation passed; raw response bytes unchanged; response SHA-256 `46153ffd72ad1766ee6d1ae8e2b86d99a85a044387523c7700bdbeb1a709b302`.
- Successful live run used the actual saved incident source, not a repaired assessment or mock. It verifies Codex 0.163.0 on this machine under approved runtime permissions. It is not a fresh caption fetch, Claude verification, original-computer/0.153.4 verification, semantic fact-check, or proof of host skill isolation. The live stream contained no warning items; the precise original warning regression is proved separately by native-event fixture red→green and upstream semantics.
- [Persisted design/cold-review audit](<docs/design-audits/2026-10-22-evaluator-citation-repairs-aposd.md>) records the resolved discriminator defect, legacy compatibility pin, accepted diagnostic-hook tradeoff and final review scope.

### Constraints / observations
- No active Beads workspace; do not initialize one.
- No commit authorization. No host credential/configuration modifications; no silent billable evaluator calls.
- Original machine/version and full Codex event stream are unavailable. A local replay is not full-video recovery.
- The incident diagnostic intentionally asserts old broken behavior; retain it as historical RCA evidence rather than changing its output to imply recovery.

## Commit-workflow follow-up — 2026-10-22

- After implementation, the user invoked `/git-commit` and approved four logical commits, feature-branch push and the draft-PR/review workflow. Earlier no-commit scope statements describe the original implementation authorization, not this later explicit permission.
- Branch: `fix/accept-nonfatal-codex-warnings`, based on `1222923`. Groups: native warning decoder; source-ID protocol plus strict v1 assets; real-flow probe plus documentation; RCA/plan/progress/audit evidence. Generated transcripts/reports remain ignored.
- Git initially inferred a local-hostname author because no explicit identity was configured. Before any push, the user selected the existing repository identity `kebaux <kebaux@proton.me>`; corrected the single unpushed commit and supplied identity per command, without editing global Git configuration.
- Fresh full working-tree suite before committing: 168 discovered, 167 passed, one native-Windows skip; 11.539s, exit 0. First two committed snapshots were separately archived outside the checkout, asserted actual module provenance and passed their full suites (145 and 163 discovered, respectively; each one Windows skip).
- Final committed product snapshot `4513f29` was independently archived outside the checkout and passed all 168 tests (167 passed, one Windows skip), 11.390s, exit 0. Built wheel and sdist from that archive with `python -m build --no-isolation`; asserted both schema assets and source-distribution probe/test inclusion, exit 0.
- GitHub CLI authenticated successfully for the existing repository. Local `cubic` executable is absent from PATH. No cubic review, silent installation, substitute cubic result, ready transition, or cloud review is claimed. The draft PR must remain draft until that preflight gate is resolved or the user explicitly chooses otherwise.

## Running Notes

### 2026-10-22
- User authorized proceeding with RCA recommendations. Plan is intentionally two phases; only the persisted citation protocol needs an architectural decision. Execution uses fresh agents after cold plan review.
- Cold review completed against actual decoder, request/evidence validator, lookup generation, schemas, packaging and RCA. Parent accepted substantive plan corrections: keep ID-only v2 and strict legacy v1; preserve conditional evidence requirements; do not equate stable source identity with semantic correctness. No tasks cut/deferred or product files edited.
- Native catalog feasibility resolved as unsupported/unobserved on the documented local surface; do not equate app-server/debug paths with exec. After explicit user usage/credit consent, Phase 2 changed to the actual evaluator-flow probe, with cold amendment review and the unsupported catalog guarantee clearly narrowed.
- User granted a separate diagnostic attempt after immediate native startup failure, then approved exact-command wider-filesystem retry through the tool permission mechanism. No application-level automatic retry or bypass of schema/evidence validation was added.
- Parent accepts the final Phase-1 and Phase-2 independent code reviews; package/runtime proof and live-environment outcomes remain separately labeled. No commit made.
