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
