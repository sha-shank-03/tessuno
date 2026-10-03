# Issue drafts, not created issues

1. Resolve public name, maintainer, external contribution workflow and security route
   Completed decision: Apache-2.0 for original code, documentation and synthetic examples.
   Remaining acceptance: identity decisions and comprehensive SPDX/license validation; no publication implied
2. Complete host adapter qualification
   Acceptance: current Codex docs, generated snapshots, exact host version and mandatory scope/gate
   negative tests; preserve non-qualified status until actual isolated smoke tests pass
3. Build original iOS executable fixtures and practical role evals
   Acceptance: seeded compile and regression failures, truthful evidence summary and independent
   review; actual Xcode/toolchain validation on approved Mac; no private app code or accounts
4. Implement trusted evidence provenance and release policy
   Acceptance: authenticated producer/workflow, exact closure/config digests, all attempts, current
   scope approval, redaction/integrity/expiry/revocation checks and invalidation after edits
5. Review and enable isolated CI
   Acceptance: independently verified offline untrusted-worker boundaries; pinned dependencies,
   no secrets/host mounts/write tokens; no actual enablement without authorization
6. Prepare a private candidate for independent review
   Acceptance: reproducible archive/readback, exact diff, license inventory, all gaps explicit
7. Consider additional platforms and capabilities
   Acceptance: separate qualification for each host; build/regression, accessibility, localization,
   StoreKit and device/account profiles individually gated; no scope expansion by implication
