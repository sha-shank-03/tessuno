# CI policy: scoped Lane A; disabled Lane B

Lane A is limited to the exact reviewed-source controller below. Lane B remains disabled.
The original activation plan and both bounded run records are retained below; they do not
authorize another dispatch or validation of a newer source revision.

## Recorded source integration and later Lane A run: 2026-10-03

The separately owner-approved [run 37132277113, attempt 1](https://github.com/sha-shank-03/tessuno/actions/runs/37132277113)
checked source `f0ff1194370305d89d28dbe56d44f0c90434575d` using controller commit
`cddc1cbab71ceaa9f5366b74edcb716924306da1`, merged in
[PR 19](https://github.com/sha-shank-03/tessuno/pull/19). All job steps succeeded:
98 tests, zero skips, 10 objects, 86 generated outputs, expected qualified-publication
rejection (exit 1), Lane B/exact-controller checks and clean source status. Build root
digest was `bfd749a67c6ac5022f5eea219cf64159729b0a465aa360aa221b70815aa14dd7`.
The job took 123 seconds with Python 3.12.15 and Node 24.21.0; no artifacts were uploaded.

After that matching pass, [PR 17](https://github.com/sha-shank-03/tessuno/pull/17) merged
at recorded main `a55e9e6f1e3a32882b73e002c5126c71b7706970`. Its Git tree,
`fb17cf1b47b3cf991cae94bec27ff4191aa8ac34`, is identical to the checked source tree.
The source landing restored the original workflow bytes in a history-preserving
commit, without a reset, squash, rebase or force push. Workflow SHA256 is again
`aa96215d825cc9e801e6dc155160a6b1044b66fe02d35bd64549d1dc534819d9`, and the active
controller selects `ade193beda810f85ac38fa008f25f7261c272b23`, not current main.
Repository settings were unchanged during this later bundle.

Both one-run authorizations are consumed. Do not repoint or dispatch the controller
on the strength of these records. Later source edits require their own review and
validation. Neither run executed a model, Xcode, an Agent host adapter or a release;
runtime qualification, trusted evidence and untrusted Lane B enforcement remain unresolved.

## Historical first Lane A execution: 2026-10-03

[PR 18](https://github.com/sha-shank-03/tessuno/pull/18) merged only the approved two-file
bootstrap. Controller/main commit `a865822680cc390e9e5e5ec807f5d0dc6d33a8b2` retains
workflow SHA256 `aa96215d825cc9e801e6dc155160a6b1044b66fe02d35bd64549d1dc534819d9`.
The owner-authorized [single run, attempt 1](https://github.com/sha-shank-03/tessuno/actions/runs/37121608051)
succeeded against only `ade193beda810f85ac38fa008f25f7261c272b23`: 91 tests, zero skips,
10 objects, 45 generated outputs, expected publication rejection and clean source status.
The one job took 82 seconds with Python 3.12.15 and Node 24.21.0. No artifacts were uploaded.

Final settings readbacks confirmed selected actions limited to the three SHA refs below,
SHA pinning required, broad GitHub-owned/verified exceptions false, read-only defaults,
PR approval false and `all_external_contributors` fork approval. The API required a
temporary stricter `local_only` mode before selecting the exact list; no dispatch occurred
during configuration, and all final readbacks passed before dispatch and after completion.
These are recorded settings, not a guarantee against a future trusted writer changing them.

At this first execution, PR 17 was not yet merged and the later source-viewer and
exact-controller admission changes had only local checks. The first 91-test run did
not validate them; the later 98-test run above checked their exact accepted source.
Browser review is separate from these Lane A checks and grants no runtime qualification.

## Disabled Lane B design

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
network defaults do not prove network denial. Enable no Lane B execution until a real environment and controls
are independently reviewed. A YAML job that merely runs these scripts would not establish trust.

## Lane B activation diff to prepare later

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

## Historical first-bundle Lane A bootstrap; untrusted Lane B remains disabled

**Historical activation condition (the approved one-run bundle is complete):** This bootstrap adopted only the reviewed-source Lane A exception
after owner authorization of its exact merge to main, the scoped repository settings and one
manual run, subject to the readbacks below. That authorization has been consumed by the
first recorded run; subsequent source integration grants no further execution authority. The original requirements above
remain effective for Lane B. Their all-activation blocker has only this documented A exception;
no Agent, Skill, Recipe, Pack, evidence, publication or release contract changes.

The sole controller path is `.github/workflows/reviewed-source-validation.yml`. Its bytes
are identical to independently accepted inert proposal commit
`cdb9b22660445e7429df7775d16092117fead0c2`, with SHA256
`aa96215d825cc9e801e6dc155160a6b1044b66fe02d35bd64549d1dc534819d9`.
The historical inert-proposal header comments are preserved to retain that reviewed digest;
the controller path, repository settings and dispatch guards determine activation. No disabled
copy is added by this bootstrap. Lane B's separate disabled proposal remains unchanged.

### Lane A: manually validate one exact reviewed source commit

The first checked source was `ade193beda810f85ac38fa008f25f7261c272b23`, the independently accepted
bounded source integration then proposed in [PR 17](https://github.com/sha-shank-03/tessuno/pull/17).
That bootstrap started from main `f19a87ab6d1a390f0c1848b2338b21301163494e`; it did not
merge PR 17 or rewrite any existing branch. The workflow controller and checked
source are separate identities, both recorded in run logs.

Bounded Lane A configuration:

- Only `workflow_dispatch`; only `sha-shank-03` as both actor and rerun actor, on main
  in public `sha-shank-03/tessuno`. No arbitrary commit input, PR trigger or matrix.
- Checkout the literal reviewed SHA and verify it before checking source. No submodules,
  LFS, persisted Git credentials or checkout of a changing branch/PR merge ref.
- Empty default token permissions; the only job grants `contents: read`, with all other
  scopes absent. No repository, organization, environment, application or provider secrets,
  PAT, OIDC, signing, environment, deployment, package/release publication or PR approval.
- Three official actions pinned to full commit SHAs; Python 3.12.15 and Node 24.21.0.
  The existing seven-package development lock is consumed from that same reviewed SHA,
  requiring hashes and wheels only. No dependency upgrade, source-distribution fallback,
  pip cache, package-manager cache, Actions cache, artifact upload or privileged consumer.
- One standard `ubuntu-24.04` job, ten-minute job limit, bounded setup/check steps and
  dependency retry/time limits. Constant concurrency group; no automatic retries or
  cancellation of a running attempt. Preserve failed, timed-out and skipped run records.
- Run the reviewed source-hygiene, validation, unittest and deterministic-build commands;
  require publication rejection, check the still-inert lane B proposal and source status.
  That first checked source had 91 structural/synthetic tests; the later accepted source has 98.
  CI does not call Xcode,
  Apple services, a model, an Agent host adapter or any deployment service.

"No secrets" excludes application/repository secrets, not every platform credential.
Checkout/bootstrap still uses the platform's ephemeral read-only `GITHUB_TOKEN`;
GitHub also supplies internal run-service credentials. No credential-free containment
claim follows from `persist-credentials: false` or a missing `secrets` expression.

Lane A would accept GitHub-hosted image/bootstrap and network trust. The runner image
changes over time; exact language/action versions are not an immutable runtime image.
Standard hosted VMs have outbound network access and passwordless sudo. This proposal
does not enforce offline execution, remove Docker/sudo capability, prove token absence,
or implement the proposed 1 GiB memory/scratch and 10 MiB log quotas. Its scope is reviewed
first-party source validation on a disposable runner, not hostile-code containment.

### Repository-wide workflow admission prerequisite

The owner/ref guard protects this job only. An action allowlist does not prevent other
workflows with inline `run` steps; local/owner actions may also be permitted. Read-only
defaults can be overridden by a workflow writer. Require trusted owner review of every
workflow, trigger, permission and local-action change on every same-repository branch.
Do not add a writer or approve an untrusted fork run as part of A. Privileged events or
consumers remain excluded. These are admission procedures, not a universal execution
allowlist or an implemented branch-protection guarantee.

The 2026-10-03 read-only inventory found Actions disabled, zero registered workflows,
zero runs and no `.github/workflows` files across all nine same-repository branch heads
and open-PR heads (nine distinct commit trees; no tags). At that preparation snapshot the fork policy was
`first_time_contributors`. The approved activation plan required rechecking the inventory and changing
the policy to **Require approval for all external contributors**
(`all_external_contributors`); read back the effective value. Prior contribution can
bypass first-time-only approval. Leave all untrusted fork runs unapproved under A.
Any newly discovered workflow or same-repository writer requires fresh scope review.
[GitHub documents these policy limits](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository).

### Reviewed version and one-run advisory disposition

Select and assert [Python 3.12.15](https://www.python.org/downloads/release/python-31215/),
the 2026-09-30 security release. The official
[Python versions manifest](https://github.com/actions/python-versions/blob/main/versions-manifest.json)
listed a Linux 24.04 x64 build at preparation time. Local foundation checks used the
existing Python 3.12.13 environment; the later recorded Lane A run used 3.12.15 and
executed the three pinned actions. That run grants no vulnerability clearance.

| Action | Exact commit |
| --- | --- |
| `actions/checkout` | `3d3c42e5aac5ba805825da76410c181273ba90b1` (v7.0.1) |
| `actions/setup-python` | `9191ea1a55b1e7028943ee5647bf579e1182b42d` (official upstream security fixes after v7.0.0) |
| `actions/setup-node` | `820762786026740c76f36085b0efc47a31fe5020` (v7.0.0) |

The previous setup-python v7.0.0 lock contains `fast-xml-parser` 5.9.3, matching
[GHSA-8r6m-32jq-jx6q](https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-8r6m-32jq-jx6q).
Replace that pin with the narrow
[two-commit upstream security update](https://github.com/actions/setup-python/compare/5fda3b95a4ea91299a34e894583c3862153e4b97...9191ea1a55b1e7028943ee5647bf579e1182b42d).
Its lock and license metadata select patched 5.10.1 and Undici 6.28.0; both action
bundles were updated upstream. Action inputs, Node24 runtime, root MIT license and
cache-control source are unchanged. This is an official commit pin, not a new published
release tag. Keep the Python cache input unset, Node caching false and cache-mode none.
The exact replacement and dependency/license delta were independently accepted with the
documented residual one-run risk. Lock metadata and static bundle inspection do not prove
source-to-bundle equivalence or vulnerability freedom; no action bundle was executed locally.

The unchanged checkout and setup-node locks contain Undici 6.27.0, matching the July
advisories [retry response framing](https://github.com/nodejs/undici/security/advisories/GHSA-8xcm-r25x-g524),
[blob content-type injection](https://github.com/nodejs/undici/security/advisories/GHSA-m8rv-5g2x-5cg5)
and [cookie attribute injection](https://github.com/nodejs/undici/security/advisories/GHSA-v3r7-h72x-cjcm).
No reachable exploit in this fixed-source lane has been demonstrated. Reviewed bounded
disposition: one owner-approved run with literal source/runtime/action inputs, disabled
caches, reviewed first-party code and ordinary official-upstream network trust; no
untrusted blob/header/cookie input or downstream proxy feature is supplied by Tessuno.
Those constraints reduce exposure by inference, not a full dependency reachability proof.
Independent review accepted this documented one-run disposition; explicit owner acceptance
is included in the bundled activation approval. The exception cannot cover
untrusted contributions, new inputs, later pins or later source/controller revisions.

All action roots declare MIT; transitive packages retain their own license expressions
and are not relicensed under Tessuno's Apache-2.0. This is targeted advisory/metadata
review, not an exhaustive vulnerability scan, independent bundle rebuild or execution test.

### Lane B: untrusted contribution or evaluation execution

The existing requirements remain: protected external harness/scorer and acceptance policy,
reviewed immutable runtime/image/wheelhouse, denied egress after acquisition, isolated
credentials/mounts/socket, enforced CPU/memory/disk/log/time budgets, demonstrated child
cancellation and adversarial fork/same-repository/injection/artifact-poisoning checks.
The PR 14 proposal included in the reviewed PR 17 source remains disabled, hard-blocked
and unchanged. Adding automatic PR execution, arbitrary source selection, contributed
policy or model/host execution is a new B-scope review, not an extension granted by A.

Neither lane alone authenticates evidence or establishes Agent/runtime/enforcement
qualification. `trust_evidence`, `qualify` and `publication_gate` remain rejecting.
Raw-source/browser, real iOS/app/model/producer and release qualification gates stay open.

### Historical bundled owner approval and execution plan

One explicit owner approval covers this exact two-file bootstrap, A's hosted-runner
assumptions and documented one-run residual advisory disposition, the scoped repository
settings and one manual run. Within that approved scope, proceed through these steps
without repeated generic approval. Failed or changed readbacks stop execution and require
resolution/review; this approval does not authorize reruns or scope expansion.

1. Review the final two-file activation diff and unchanged workflow digest. Confirm supported
   hosted Actions syntax/inputs against the accepted configuration; local YAML/bash parsing
   is not a hosted execution verdict. Keep Actions disabled while preparing the merge.
2. Read back public `sha-shank-03/tessuno`, default branch main, current main identity and
   all branch/PR workflow paths. Inventory registered workflows and existing same-repository
   writers; resolve unexpected workflows or authority before enabling anything. No canonical
   contract/tool, existing source branch, PR 17 or original Lane B proposal changes.
3. Publish and merge only the approved two-file bootstrap into main while Actions remains
   disabled. Manual dispatch needs the controller on the default branch. Read back the
   actual controller/main commit and exact workflow bytes/digest; record both identities.
4. Before enabling Actions, set and read back `approval_policy: all_external_contributors`,
   `default_workflow_permissions: read` and `can_approve_pull_request_reviews: false`.
   Set selected-action policy to the three exact SHA refs above, `github_owned_allowed: false`,
   `verified_allowed: false` and `sha_pinning_required: true`; no broad action exception.
   Enable Actions only after inventory and admission-policy readbacks pass, then verify every
   effective setting again. Keep all untrusted fork runs unapproved and workflow/permission/
   local-action changes under trusted owner review. The allowlist does not block inline code.
   No secret, production environment, new writer, self-hosted runner or billing setup.
5. After those matching readbacks, perform exactly one `workflow_dispatch` by `sha-shank-03`
   from main, bound to the recorded controller SHA and workflow digest, validating only
   `ade193beda810f85ac38fa008f25f7261c272b23`. Recheck main immediately before dispatch and
   verify the resulting run's controller identity; abort/cancel on drift. Actor and rerun
   actor must both be the owner. No second attempt or automatic retry is authorized.
6. Record run URL, attempt, controller/source SHAs, image/runtime identities, every job/step
   outcome, test count, expected publication rejection and build receipt. Skips, parser/setup
   failures, timeouts or partial checks provide no validation verdict. This is not a required
   PR 17-head status check. No source merge, deployment, release or qualification follows.

The pinned checked source forbids all live workflows in its own snapshot; those tests
were unchanged for the first recorded run. The merged source integration replaces that
blanket assertion with admission of at most the exact approved controller filename and
whole-file SHA256 above. Absent workflows remain accepted for source-only fixtures.
Changed controller bytes, extra paths, directories and symlinks reject before admission.
Negative tests cover trigger, permission, source/action pin, extra-file and symlink changes.
This contributed consistency check is not protected policy or a malicious-code security
verifier. It grants no dispatch authority and never accepts a newer source in the controller.

Public standard runner minutes are currently free; the proposal uses no larger runner,
cache/artifact storage, deployment or model call. Budget: one job per explicit dispatch,
ten-minute configured timeout, one active job. Hosted public Ubuntu allocation is currently
4 vCPU, 16 GB RAM and 14 GB SSD, not a custom per-process quota. Cancellation may take
additional platform shutdown time. Private visibility, paid runners, storage or provider
calls need a separately approved budget. No account-wide billing change is proposed.

Sources checked during proposal preparation:

- [Manual dispatch and default-branch requirement](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
- [Dispatch source/ref semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch)
- [Hosted runner resources and privileges](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- [Permissions, timeout and cache-mode syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Action pinning and untrusted-code risks](https://docs.github.com/en/actions/reference/security/secure-use)
- [Repository action allowlists](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [Hash-checked wheel installation](https://pip.pypa.io/en/stable/topics/secure-installs/)
- [Public standard-runner billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Workflow cancellation behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-cancellation)

## Issue 6 inactive candidate

Review `docs/ci/validation.yml.disabled`. It is outside `.github/workflows`, has an
inert suffix, disables its only job with `if: false`, and places an unconditional
exit1 before any prospective dependency install or candidate execution. Actions
was disabled when this Lane B draft was prepared; the later scoped Lane A activation
is recorded above. Lane B's template remains unchanged and has never been run.
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
is pinned to historical main `f19a87ab6d1a390f0c1848b2338b21301163494e`, which does
not contain this parity tool.
A later protected harness revision must be independently bound before activation.
No cache/save/restore or artifact consumer is introduced.

### Command parity and coverage

`python tools/check_ci_proposal.py` parses inert YAML with duplicate-key rejection
and checks selected policy constraints. It is a consistency checker, not an Actions
schema validator, complete malicious-YAML auditor or isolation verifier. No
GitHub actionlint binary/dependency was acquired. Activation requires authoritative
workflow validation in the protected review environment as well.

`python tools/ci_checks.py` executes local source-hygiene, schema/semantic validation,
the discovered unittest suite (98 cases in the recorded merged source)
and static build, then requires publication to exit1. Its tests
include negative schema/path/duplicate-key/manifest/evidence gates, deterministic
archive/build/readback and synthetic fixture oracles. Format check means Python
syntax, JSON validity/duplicate rejection, UTF8/LF/final-newline/trailing-whitespace
checks on code/schema files; it is not an opinionated formatter or JS runtime audit.
The merged PR 17 source combines the reviewed adapter/export, diagnosis, Xcode fixture,
catalog and source-viewer features with the scoped controller. The later recorded Lane A
run checked this exact 98-test source; the earlier run checked only the 91-test source.
The initial Issue 6 parity snapshot had 36 tests; that is a historical count.

All current cases remain structural/synthetic fixture checks. They do not demonstrate
network denial, secret absence, token removal, host sandbox enforcement, signing,
macOS/Xcode compile/runtime, real Agent/model evaluation or trusted evidence.
The local parity helper executes candidate scripts/tests with a direct-process
120second timeout (publication30seconds). It does not constrain descendant
processes, memory, filesystem, egress or logs and must NOT be mistaken for an
isolation harness. In an eventual untrusted lane, a protected external orchestrator
must run fixed commands against the candidate; contributed ci_checks.py/test output
cannot determine the trusted policy or award acceptance.

### Resource plan and concrete activation gates

The initial local 36-test Issue 6 snapshot took 3.364 seconds; this is historical, not
a performance measurement of the current suite. No portable memory/disk/CPU peak is measured.
Plan one disposable job, no matrix, ten-minute job limit; protected isolation target
2vCPU,1GiB RAM,1GiB scratch and10MiB retained logs, with acquisition separately
bounded. These are proposed budgets, not enforced by this YAML or local helper.
Owner must review actual measured limits/runner cost before Lane B activation. No spending.

Before any Lane B activation: independently review exact candidate/action/dependency
sources and license inventory; supply immutable runner/image/Python/wheelhouse and
protected harness digests; demonstrate denied egress after acquisition and absent
secrets/write tokens/host mounts/socket/credential material before candidate code;
test adversarial fork/same-repository PRs, shell injection, oversized output,
timeouts/child cancellation, memory/disk exhaustion and artifact poisoning in that
isolation; preserve every attempt/skipped check with redaction and exact digests;
validate workflow grammar/policy and protected branch/reviewer ownership; obtain
separate owner authorization to replace Lane B blockers and permit its execution. A hosted-runner
YAML alone meets none of the offline enforcement gates. No privileged consumer.
Issue6 remains open; independent security review is required even for draft push.

The bounded review fixes freeze protected/candidate checkout refs and paths plus
the intended runner label; reject continue-on-error and step-condition overrides;
and reject scanned source-directory symlinks before file reads. Synthetic negative
tests cover each change. Root aliases resolve consistently. These remain limited
consistency/hygiene checks, not a general malicious-YAML auditor or host sandbox.
