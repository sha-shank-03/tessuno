# Tessuno preparation history and source preview

The owner selected Tessuno on 2026-10-03. This preparation preserves the reviewed
Apache-2.0 scaffold rather than creating a replacement implementation. It starts with
iOS Studio and leaves cross-stack execution, adapters and qualification on the roadmap.
The initial unpublished preparation and subsequent engineering review are historical
stages. Maintainer and contribution/security triage owner is GitHub account `sha-shank-03`.
Public source scope and planned settings are recorded in source-preview-policy.md.
The repository is now public; the later two-file CI bootstrap and one fixed-source run
are recorded in ci-proposal.md. The preparation facts below retain their historical scope.
The newer combined candidate remains local for review and has not been checked by hosted CI.

## Source and local history

The Library source is `agent-library-prototype-apache2-source.zip`, version 1,
156288 bytes, SHA-256
`63e930e4b94bd2a782f6e3119c597118362337cb21404a27e233230cfb0a9df3`.
The supplied source revision is `f931f0fd52938be9a31df8a1cab6aa8ba90d4cec`.
The ZIP excludes `.git`; the local repository therefore has a new import commit,
not recovered original Git history. DELIVERY-MANIFEST.json and DELIVERY-REPORT.txt
are preserved historical receipts for the original source, not the modified candidate.
Do not describe their old hashes or review as approval of this Tessuno diff.

Branding changes touch development guidance, contribution/security documentation and
catalog presentation. Subsequent review fixes normalize caller roots consistently and
pin development dependencies, without changing canonical schemas, object identifiers,
fixtures, publication behavior, LICENSE or third-party notices. No domain or
GitHub organization ownership is claimed. The owner reports tessuno.com registered;
tessuno.dev and the exact GitHub handle remain unverified. No purchase is proposed.

## Mac development setup

Use Python 3.11+ in a virtual environment outside the source tree. From the repository
directory, explicit setup is:

```sh
python3 -m venv ../.tessuno-venv
. ../.tessuno-venv/bin/activate
python -m pip --isolated install --require-hashes -r requirements-dev.txt
```

On Windows, activate `..\\.tessuno-venv\\Scripts\\Activate.ps1` in PowerShell.
The lock pins all seven packages and the published release hashes for platform-specific
wheels from official PyPI. Binary-only installation fails closed if no matching wheel
exists; it never builds an unreviewed source distribution. No dependencies are vendored.
This is a development dependency lock, not a protected offline runner or CI qualification.

macOS aliases `/var` to `/private/var` and `/tmp` to `/private/tmp`. The original source
had a lexical/resolved root mismatch. Roots now normalize consistently before relative
path operations, so ordinary tests work with the default temporary directory. Descendant
symlinks remain rejected. If a separate test scratch directory is desired, use:

```sh
mkdir -p ../.tessuno-test-tmp
export TMPDIR="$(cd ../.tessuno-test-tmp && pwd -P)"
```

Always keep `TMPDIR` outside this repository. Tests copy the source tree into temporary
fixtures; putting scratch beneath the source would recursively copy the fixtures.
Validation and build commands then operate offline:

```sh
python tools/validate.py
python -m unittest discover -s tests -v
python tools/build.py
python tools/validate.py --publication
```

The last command must fail closed: it is the unchanged qualified-release/execution gate.
Local tests and deterministic generation do not qualify a host, authenticate evidence or
establish runtime containment. The owner's separate public source instructions authorize
the bounded reviewed source preview, not a verified agent release. No executable host
adapter, model eval or Xcode run was established by this initial preparation. The later
manual CI run checked reviewed source only and established no runtime qualification.

## Publication and review boundaries

At initial preparation the candidate was local with no remote configured, and creation/push
were unverified. Repository creation and the later bounded CI bootstrap are now recorded;
private reporting settings remain unverified here. Independently review the exact launch diff before
the bounded source-only setup. Maintainer ownership and contribution process are documented;
SECURITY.md records the private reporting route as unverified and withholds a reporting URL.
Only settings/content readback can justify updating launch status. No monitored-reporting
claim may be made without notification verification, and no response SLA is promised.

Implement comprehensive SPDX/license validation and trusted producer, integrity, expiry,
revocation and host checks before qualification or verified-release claims. The existing
publication gate remains an unconditional rejection; inspectable public source never
bypasses it. Lane B in docs/ci-proposal.md remains disabled, and the development lock is not a
qualified runner. No catalog deployment or GitHub mutation is performed by these docs.

The eight issue texts record the original drafts. The subsequent CI bootstrap was a separately
reviewed and authorized change described in docs/ci-proposal.md. No secrets, credentials, private
application details, unrelated projects or cancelled studio services belong here.
