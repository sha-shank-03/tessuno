# Disabled CI design proposal

No .github/workflows job is enabled and no GitHub run occurred. This is a reviewable design only.
Do not copy candidate commands into privileged pull_request_target or workflow_run jobs.

Untrusted pull-request lane:
- Fresh disposable runner, no protected environment/secrets, no production data or host home
- Empty permissions by default; if checkout needs contents:read, use only a read-only ephemeral token
  for acquisition and remove credentials before candidate execution; persist-credentials false
- No Docker socket, privileged containers or host mounts; default-deny egress after acquisition
- Trusted runner image and validator/harness/scorer from a reviewed protected digest, not the PR
- Bound time, memory, output and dependency setup; pin all allowed dependencies/actions by immutable
  digest and review their sources; candidate code/build/fixtures remain untrusted throughout
- Run shape/semantic checks, negative fixtures, reproducibility and sanitized readback
- No uploads, release, deploy, comments, signing or privileged artifact-consumer path

Protected review lane:
- Authenticate candidate digest and producer separately; never execute candidate artifacts
- Preserve all attempts, errors and skipped checks; stale approval is rejected
- Publication is separate owner-authorized work and remains blocked by identity and trusted-release decisions

Enforcing runner isolation and offline dependencies has not been implemented. A hosted runner's
network defaults do not prove network denial. Enable nothing until a real environment and controls
are independently reviewed. A YAML job that merely runs these scripts would not establish trust.

## Tessuno activation diff to prepare later

Keep this proposal disabled. A later bounded change should add a reviewed dependency
lock with hashes and an offline runner image; bind validator/harness/scorer to a
protected digest; and add a pull_request-only job after isolation is demonstrated.
Pin checkout to a reviewed immutable commit, set persist-credentials: false, and
use contents: read only for acquisition with all other permissions empty. Remove
acquisition credentials and deny network before any candidate code executes. Bound
time and resources; run validation, negative tests, deterministic build and readback.
Do not add pull_request_target, workflow_run, secrets, write tokens, artifact consumers,
comments, Pages, deployments, signing, package publishing or production environments.
Ordinary hosted-runner YAML does not enforce the required offline boundary. The runner
implementation, dependency license inventory and protected configuration remain blockers.

## Issue 6 inactive candidate

Review `docs/ci/validation.yml.disabled`. It is outside `.github/workflows`, has an
inert suffix, disables its only job with `if: false`, and places an unconditional
exit1 before any prospective dependency install or candidate execution. Actions
was read back disabled on2026-10-03. No run or setting change is part of this work.
Do not move/rename this file or remove these stops during review.

The template permits only pull_request for main, default empty permissions and
contents:read for acquisition; no secrets references, deployment, environment,
uploads, privileged events or self-hosted runner. Checkout has credentials,
submodules and LFS disabled. Merge-ref number is used only as a structured action
input, not interpolated shell code. Candidate checkout remains untrusted.
Official immutable references observed via GitHub API:
checkout v4.2.2 `11bd71901bbe5b1630ceea73d27597364c9af683`;
setup-python v5.6.0 `a26af69be951a213d495a4c3e4e4022e16d87065`.
Pinning is identity evidence, not complete action-source/security/license review.
Python3.12.13 is exact-version selected; ubuntu-24.04 and setup-python's acquisition
are not an immutable reviewed offline runtime image. Those remain activation gaps.

Dependencies reuse the existing seven-package full hash lock. Prospective offline
installation requires wheels only, --no-index and --require-hashes from the
protected lock, never the contributed lock. `/opt/tessuno-reviewed/wheels` is a
proposed location, NOT an existing/verified image or wheelhouse. Protected source
is pinned to main's current snapshot, which does not contain this new parity tool.
A later protected harness revision must be independently bound before activation.
No cache/save/restore or artifact consumer is introduced.

### Command parity and coverage

`python tools/check_ci_proposal.py` parses inert YAML with duplicate-key rejection
and checks selected policy constraints. It is a consistency checker, not an Actions
schema validator, complete malicious-YAML auditor or isolation verifier. No
GitHub actionlint binary/dependency was acquired. Activation requires authoritative
workflow validation in the protected review environment as well.

`python tools/ci_checks.py` executes local source-hygiene, schema/semantic validation,
36 unittest cases and static build, then requires publication to exit1. Its tests
include negative schema/path/duplicate-key/manifest/evidence gates, deterministic
archive/build/readback and synthetic fixture oracles. Format check means Python
syntax, JSON validity/duplicate rejection, UTF8/LF/final-newline/trailing-whitespace
checks on code/schema files; it is not an opinionated formatter or JS runtime audit.
Main does not contain the unmerged adapter/export, diagnosis, Xcode or browser-filter
features. None is silently incorporated. No external runs occurred.

All36 cases are local structural/synthetic fixture checks. They do not demonstrate
network denial, secret absence, token removal, host sandbox enforcement, signing,
macOS/Xcode compile/runtime, real Agent/model evaluation or trusted evidence.
The local parity helper executes candidate scripts/tests with a direct-process
120second timeout (publication30seconds). It does not constrain descendant
processes, memory, filesystem, egress or logs and must NOT be mistaken for an
isolation harness. In an eventual untrusted lane, a protected external orchestrator
must run fixed commands against the candidate; contributed ci_checks.py/test output
cannot determine the trusted policy or award acceptance.

### Resource plan and concrete activation gates

Observed local36-test run took3.364seconds; no portable memory/disk/CPU peak measured.
Plan one disposable job, no matrix, ten-minute job limit; protected isolation target
2vCPU,1GiB RAM,1GiB scratch and10MiB retained logs, with acquisition separately
bounded. These are proposed budgets, not enforced by this YAML or local helper.
Owner must review actual measured limits/runner cost before activation. No spending.

Before any activation: independently review exact candidate/action/dependency
sources and license inventory; supply immutable runner/image/Python/wheelhouse and
protected harness digests; demonstrate denied egress after acquisition and absent
secrets/write tokens/host mounts/socket/credential material before candidate code;
test adversarial fork/same-repository PRs, shell injection, oversized output,
timeouts/child cancellation, memory/disk exhaustion and artifact poisoning in that
isolation; preserve every attempt/skipped check with redaction and exact digests;
validate workflow grammar/policy and protected branch/reviewer ownership; obtain
separate owner authorization to replace blockers and enable Actions. A hosted-runner
YAML alone meets none of the offline enforcement gates. No privileged consumer.
Issue6 remains open; independent security review is required even for draft push.

The bounded review fixes freeze protected/candidate checkout refs and paths plus
the intended runner label; reject continue-on-error and step-condition overrides;
and reject scanned source-directory symlinks before file reads. Synthetic negative
tests cover each change. Root aliases resolve consistently. These remain limited
consistency/hygiene checks, not a general malicious-YAML auditor or host sandbox.
