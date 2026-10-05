# Offline evaluation capture inventory

`tools/check_evaluation_capture.py` checks supplied capture records against a separately
selected policy. It addresses roadmap item 4's evidence-inventory gap: a successful
result file or evaluator's final answer cannot replace admission and tool-request records.
This checker collects nothing, executes no payload and calls no model, Xcode or network.
It cannot recover a missing historical transcript. Preserve existing qualified results
and original receipts rather than rewriting them or rerunning an evaluation to fill a gap.

```sh
python tools/check_evaluation_capture.py capture.json --policy policy.json --root /path/to/sanitized-capture
```

All supplied paths are relative to `--root`; absolute paths, traversal, URLs and symlink
components are rejected. Each consumed artifact is capped at 4 MiB and a transcript at
500 events. Use an immutable local snapshot; these checks do not prevent concurrent
filesystem mutation or provide OS containment. Referenced bytes are never printed.
Only supply records already reviewed for safe handling; this tool is not a redactor.

## Input records

The closed [schema](../schemas/evaluation-capture.schema.json) defines four record kinds.
Every record has `schemaVersion: "1"`; unknown fields and duplicate JSON keys reject.
All digests are lowercase SHA256 of exact file bytes, not normalized JSON.
Timestamps use `YYYY-MM-DDTHH:MM:SS[.fraction]Z`, with one to six fractional digits
when present. Other offsets, compact/date-only forms, leap seconds and finer precision
are rejected explicitly; validation does not depend on optional date-format packages.

| Record | Contents |
| --- | --- |
| `evaluation-policy` | Evaluation ID, exact candidate/scope digests, fixed UTC start, total budget, maximum build count/duration, model and fresh/inherited context declaration. Selected with `--policy`, independently of the manifest. |
| `capture-manifest` | Evaluation ID, policy digest, admission/transcript references and event count. A reference is `{ "path": "relative/file", "sha256": "…" }`; missing admission/transcript must be `null`. |
| `task-admission` | Evaluation/policy identity, task and turn IDs, fixed start, model and context mode. These are declarations pending producer authentication. |
| `tool-transcript` | Evaluation/policy/task/turn identity, declared capture status, closure time and ordered events. Incomplete capture uses `captureStatus: "incomplete"`; closure may be `null`. |

Each event records a contiguous one-based sequence, unique request ID, tool name,
declared operation (`read`, `edit`, `build`, `other`), UTC request/completion times,
outcome and separate request/response artifact references. Preserve failed, denied,
cancelled and incomplete events. Unknown completion and missing response use `null`;
they remain gaps. Request and response payloads are opaque sanitized bytes, not commands
to run. The format inventories them without interpreting shell syntax or nested calls.

## What the result establishes

The checker detects identity/digest mismatches, absent or unsafe artifacts, inconsistent
event counts, gaps/reordering in sequence, duplicate request IDs, incomplete closure,
out-of-budget timestamps and excessive declared build counts/durations. Parallel events
may complete out of order, but requests must remain ordered. All declared build requests
count toward the limit, including failed, denied, cancelled and incomplete requests.
Capturing a failed action consistently does not make that action successful.

Exit `0` means `inventoryStatus: "consistent"`; exit `1` means inventory gaps; exit `2`
means the selected input/policy is invalid or unreadable. Output is deterministic and
includes manifest, policy, schema and checker digests. Zero events are a gap. No exit
status grants execution authority or qualification. Every report keeps
`trustedEvidence`, `scopeTraceVerified` and `uniqueInvocationVerified` false and
`qualificationVerdict: "BLOCKED"`.

An author can invent a self-consistent transcript, remove events and change all hashes,
or misclassify an arbitrary shell request as `read`. This tool cannot detect those acts
from supplied bytes alone. The manifest count is a cross-check, not an authenticated
terminal sequence number. Candidate/scope digests are identity declarations; this
checker does not reconstruct a candidate closure or enforce that scope. Policy selection
and model/context claims also remain unverified. Existing evidence trust and publication
gates are unchanged; this format is not accepted as trusted execution evidence.

The next engineering step is a separately reviewed producer that retains authenticated
admission and complete request/outcome records, binds their terminal sequence and exact
policy before launch, and captures approval boundaries without exposing secrets. That
requires supported capture APIs and independent verification of all attempts, redaction,
integrity, expiry and revocation. This source change installs or enables no such producer.

Tests author original synthetic records in temporary directories. They invoke only the
offline checker; no historical evaluation artifacts or private host paths are fixtures.
