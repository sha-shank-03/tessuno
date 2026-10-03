# Release-readiness evidence reference workflow

Use `core/release-readiness-audit` to inspect a supplied sanitized packet and prepare
an operator gap report. New native Skill `core/release-readiness-evidence` and Agent
`core/release-evidence-auditor` cover version/build, tests, independent review,
TestFlight feedback, crashes, metadata/privacy, migrations and mitigation. They
require only repository.read, no writes/network, and no runtime/account action.
The existing iOS Studio Pack is unchanged. This slice is complementary to diagnosis;
it is based solely on main and requires none of the unmerged adapter/diagnosis/CI PRs.

The operator procedure in SKILL.md identifies each domain's needed inputs, common
false-pass traps and the smallest next collection task. Report exact source/dirty
fingerprint and version/build, inspected evidence paths/hashes, known failures,
missing inputs and next owner/specialist. Do not choose privacy/legal declarations,
infer tester coverage from silence, infer crash-free operation from missing logs,
or mistake clean-install tests for migration/recovery qualification. A person
reviews scope before any separately requested runtime or account operation.

## Original synthetic packet evaluator

Run `python tools/evaluate_release_packet.py skills/release-readiness-evidence/fixtures/complete.json`.
Exit0 means authored inventory complete only; the report still says release BLOCKED,
trustedEvidence=false, runtimeInvoked=false and modelInvoked=false. Exit1 reports
gaps; exit2 rejects invalid input. This local evaluator is opt-in, not invoked by
Agent/Skill metadata and not a host adapter or installer. It never invokes a shell,
model, Xcode, simulator, device, portal or release controller.

The new closed release-packet schema is an example inventory wrapper, not a new
trust contract. The evaluator reuses canonical safe_path/read_json/checked_schema,
JSON Schema validation, canonical evidence_check for exact subject/scope/attempts,
and existing digests. Tests/review evidence use canonical envelopes; other domains
have original authored JSON inventory notes. A declared source digest is compared,
not independently authenticated. Version/build/scope config is bound in canonical
check.configDigest so a relabeled packet cannot reuse the toy test/review receipt.
The illustrative fixed14-day observation window compares supplied asOf, not wall
clock; it is not an Apple rule, live freshness check or recommended release policy.
No positive result admits a real app or grants release authority.

| Packet | Intended observation |
|---|---|
| complete | All8 authored inventory entries match; release still BLOCKED |
| missing | Feedback and metadata/privacy absent |
| stale | Test observation outside illustrative window; timestamp disagreement retained |
| mismatched | Tests cite another build; review declares another candidate digest |
| failure-and-not-run | Tests NOT RUN; crashes report failure; neither erased |

Negative tests also cover changed artifact bytes, future timestamps, build relabeling,
stale review scope, omitted test attempts, duplicate domains/JSON keys, unknown fields
and unsafe/symlink artifact paths. No filled checklist is scored as trusted evidence.
Source hygiene, legal/portal completeness and sandbox enforcement are not evaluated.
Concurrent hostile filesystem mutation remains outside canonical path checks.

## Provenance and remaining qualification

All packets, reports and workflow prose are newly authored fictional examples under
Apache-2.0. Existing local Testing/Release instructions were inspected read-only for
principles of exact-candidate binding, preserved failures, scoped handoff and separating
historical inspection from fresh execution. No private application code, identifiers,
logs, host configuration, Apple Skill/template or third-party text was imported.
No local role/service/profile was activated or edited. Unavailable memory summary
was not reconstructed; restricted session storage was not read.

Unit tests evaluate original synthetic inventory/evidence fixtures and canonical
contracts only. No real TestFlight feedback, crash metrics, app binary, migrations,
portal declarations, signing, real reviewer or model output was evaluated. Runtime,
producer authentication, app/device/cloud/billing qualification, legal facts and
actual release authorization remain separate. trust_evidence/qualify/publication_gate
remain fail-closed. No Actions, permission/settings change, submission or release.
