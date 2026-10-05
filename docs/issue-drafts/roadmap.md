# Roadmap and remaining qualification

Recorded source integration PR 17 merged on 2026-10-03 at main `a55e9e6f`, with the
same tree as checked source `f0ff1194`. The later separately approved Lane A run
passed 98 tests, built 10 objects and 86 outputs, and rejected qualified publication.
See [CI scope and both historical runs](../ci-proposal.md). The controller still pins
`ade193be`; this roadmap authorizes no repointing, dispatch or runtime execution.
These are source milestones, not host qualification or a live GitHub issue-state report.

1. Complete licensing and private security-reporting checks
   Completed: Tessuno name, selected maintainer, public source/contribution workflow and
   Apache-2.0 for original code, documentation and synthetic examples.
   Remaining acceptance: comprehensive SPDX/license validation and verified private reporting route;
   source publication is not qualified-release approval
2. Complete host adapter qualification
   Acceptance: current Codex docs, generated snapshots, exact host version and mandatory scope/gate
   negative tests; preserve non-qualified status until actual isolated smoke tests pass
3. Build original iOS executable fixtures and practical role evals
   Original static-library fixture and authored diagnosis examples are included in the merged source.
   Acceptance: seeded compile and regression failures, truthful evidence summary and independent
   review; actual Xcode/toolchain validation on approved Mac; no private app code or accounts
4. Implement trusted evidence provenance and release policy
   Acceptance: authenticated producer/workflow, exact closure/config digests, all attempts, current
   scope approval, redaction/integrity/expiry/revocation checks and invalidation after edits
5. Review and enable isolated untrusted CI
   Completed: two separately authorized manual fixed-source Lane A runs, as recorded above.
   Acceptance: independently verified offline untrusted-worker boundaries; pinned dependencies,
   no secrets/host mounts/write tokens; Lane B remains disabled pending separate reviewed authorization
6. Keep later source candidates independently reviewable
   Completed: reviewed PR 17 source integration and matching fixed-source CI record.
   Acceptance for later edits: reproducible archive/readback, exact diff, license inventory, all gaps explicit;
   predecessor approval never approves changed source
7. Consider additional platforms and capabilities
   Acceptance: separate qualification for each host; build/regression, accessibility, localization,
   StoreKit and device/account profiles individually gated; no scope expansion by implication
