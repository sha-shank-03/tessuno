# Inert synthetic capture-export mapping

This repository-only source tool maps an **original synthetic local export** into
the existing evaluation capture record shapes. It is not an integration with a real
producer API. It collects no session, launches no payload, writes no records, uses no
credential and changes no host, admission, security, CI or publication setting.
The new closed input contract is `schemas/capture-export.schema.json`; it changes none
of the four canonical records or their existing checker/trust gates.

```sh
python -B tools/map_capture_export.py export.json --policy policy.json --root tests/fixtures/capture-export
```

The included export, selected policy and three text files are newly authored fictional
data. All IDs, model/tool names, candidate/scope/harness hashes and timestamps are
synthetic declarations, not historical evaluation artifacts. The required origin marker
restricts the input format; it does not authenticate authorship or prove that arbitrary
supplied data is safe/synthetic. Supply only immutable sanitized source already reviewed
for handling. This mapper is not a redactor or OS containment mechanism.

The report is deterministic canonical JSON on stdout. `records` contains declarations
keyed by the fixed paths `mapped/admission.json`, `mapped/transcript.json` and
`mapped/manifest.json`. They are not written or installed. Tests explicitly materialize
these records in a disposable input copy and then invoke the existing
[offline capture checker](evaluation-capture.md). Payload references remain relative
to that same supplied root; payload bytes are neither embedded in the records nor
printed. The mapper does not copy payload files or automatically run the checker.
The mapper and fixtures are not added to the offline inspection kit. The existing
builder inventories every repository schema, so the new closed export schema is
included as inert data; the extracted kit has no mapping entrypoint or fixture.

Exit0 means the bounded translation completed without the mapper's supplied-reference
or declaration comparison gaps, not that an evaluation succeeded or that the resulting
inventory is consistent. Exit1 emits translated records plus those gaps. Exit2 rejects
invalid/unreadable inputs with empty stdout. The separate checker evaluates sequencing,
timing, closure and budgets on materialized declarations. Neither tool authenticates
producer identity, all real attempts, policy selection, operation labels or enforcement.

## Mapping and field losses

| Export field | Canonical record or report | Qualification limit |
| --- | --- | --- |
| evaluationId, policySha256 | Copied unchanged into admission/transcript/manifest | Selected policy bytes are hashed separately; disagreement is reported, not resealed |
| taskId, turnId, startedAt, model, contextMode | Admission; task/turn also enter transcript | Identity/start/model/context remain supplied claims |
| captureStatus, closedAt | Transcript, including incomplete/null closure | No missing closure is synthesized |
| requests.requestIndex/requestId/toolName/operationClaim | sequence/requestId/tool/operation, in original array order | No sorting, renumbering, shell parsing or scope verification |
| requests.requestedAt/completedAt/outcome | Copied unchanged, including null and failure/denial/cancellation/incomplete | No attempt is discarded or converted to success |
| requests.requestArtifact/responseArtifact | Relative references copied unchanged, including null response | Exact supplied hashes are compared with bounded opaque bytes; no payload execution |
| Supplied array length | Manifest eventCount | Count describes supplied records, not an authenticated external terminal |
| origin | inputOriginClaim report field | A marker is not producer or data authentication |
| claims.producerId | Unverified field-loss entry | No producer identity verification |
| claims.harnessSha256 | Unverified field-loss entry | No trusted harness/generator approval or source-to-runtime proof |
| claims.candidateSha256/scopeSha256 | Separate unverified loss entries; declared disagreement with selected policy is reported | No candidate reconstruction or observed scope enforcement |
| claims.terminalSequence | Unverified loss entry; mismatch with supplied last index is reported | A resealed contributor claim cannot prove omitted real events |
| claims.approval | Unverified loss entry | No approval/action authority is granted |
| claims.redaction | Separate raw/sanitized hashes and review claim retained in one unverified loss entry | Those referenced claims are not verified or used to replace payload integrity |
| claims.expiresAt/revoked | Separate unverified loss entries, including expired/revoked/null declarations | No trusted clock, expiry policy or authenticated revocation lookup |
| Unknown fields/versions, inline policy or another origin format | Rejected by the closed export contract | No silent field dropping or contributor acceptance policy |

Policy selection is a required independent CLI argument. Output record policySha256
always preserves the supplied export value, including disagreement; it is never
silently replaced with the selected-policy hash. Admission fields and subject claims
are compared as declarations. Output admission/transcript hashes bind newly translated
record bytes; they do not certify the source or completeness of the export.

Every successful or gap report keeps `trustedEvidence`, `scopeTraceVerified`,
`uniqueInvocationVerified`, `producerAuthenticated`, `runtimeQualified`,
`executableExportAllowed`, `redactionVerified`, `expiryVerified` and
`revocationVerified` false and `qualificationVerdict: "BLOCKED"`. Runtime/model/payload
invocation and record writes are false. A missing, expired, revoked or purportedly
approved claim cannot change those flags. All losses stay explicitly unverified.

## Limits and byte identity

Export and selected-policy files each use the existing 4MiB read cap. The closed export
permits at most500 requests. Each payload is capped at4MiB, and actual payload reads,
including rejected/repeated oversized references, consume one16MiB aggregate budget.
Repeated successfully inspected paths reuse their byte inventory; a different declared
hash for that path is still compared. Exhausted budgets leave explicit gaps. Referenced
paths reject absolute/traversal/URL/symlink inputs. The reserved `mapped` root and
namespace, including case variants, cannot be used for payload references, preventing
collisions with generated record paths on case-insensitive filesystems too.

The report hashes exact export/policy, mapper/checker/library and both schema bytes.
Those hashes identify consumed source, not authenticated producer/runtime or installed
dependency provenance. Use a stable snapshot: concurrent hostile filesystem mutation
and whole-process resource containment are not implemented here. No clock, live host
version discovery, network, subprocess, model, compiler or private capture API is used.

## Original synthetic T01–T07 coverage

| Case | Local assertion | Remaining gap |
| --- | --- | --- |
| T01 | Invented consistent export maps deterministically, changes no input and yields a consistent materialized inventory | Every trust/qualification flag remains rejecting |
| T02 | Removing requests, renumbering and resealing supplied terminal/count/hash data can remain consistent | Omitted real activity cannot be detected without independent authenticated terminal bounds |
| T03 | All five outcomes and indices remain; every declared build is retained; incomplete data stays a checker gap | A consistent inventory of denied/failed/cancelled actions is not execution success |
| T04 | An opaque shell request labeled read is copied as a declaration without executing or printing payload | Misclassification is not authenticated/detected scope enforcement |
| T05 | Distinct raw/sanitized hashes and purported review are retained outside canonical records, explicitly unverified | Redaction completeness and lineage require independent evidence |
| T06 | Changed selected policy/subject/harness claims are not silently healed; mismatches/losses stay visible | Candidate/harness acceptance and actual launch binding remain absent |
| T07 | Expired/revoked/missing producer metadata remains a declaration with all trust flags false | No authenticated expiry/revocation verifier exists |

Additional negatives cover unknown/duplicate fields, versions, non-synthetic origin,
inline policy, boolean indices/counts, strict UTC syntax, invalid Unicode (including
escaped unpaired surrogates), missing/unsafe/symlink/digest
references, reserved collisions, empty/reordered/duplicate request inventories, input
size and aggregate payload budgets, opaque non-execution and CLI exit0/1/2 behavior.
These are synthetic source regression checks, not observations of a real producer or host.

The next integration gap is an actual supported producer admission/export/capture API
with protected policy/identity ownership and independently authenticated complete
attempt, integrity/redaction, expiry/revocation and host enforcement evidence. Source
fixture work needs no new owner decision. Implementing or activating that real trust
boundary is separate work; this tool grants no permission, admission, live evaluation,
hosted CI, verified badge, release or deployment. Existing unconditional publication,
trust_evidence and executable-qualification rejections remain unchanged.
