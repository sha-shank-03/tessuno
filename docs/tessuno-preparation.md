# Tessuno development candidate

The owner selected Tessuno on 2026-10-03. This preparation preserves the reviewed
Apache-2.0 scaffold rather than creating a replacement implementation. It starts with
iOS Studio and leaves cross-stack execution, adapters and qualification on the roadmap.

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
catalog presentation. Canonical schemas, object identifiers, fixtures, validation,
publication behavior, LICENSE and third-party notices are unchanged. No domain or
GitHub organization ownership is claimed. The owner reports tessuno.com registered;
tessuno.dev and the exact GitHub handle remain unverified. No purchase is proposed.

## Mac development setup

This task uses Python 3.12 in a task-local virtual environment outside the repository.
The exact top-level dependencies in requirements-dev.txt were explicitly installed
for local validation. Dependencies are not vendored, and transitive versions are not
yet a reviewed CI lock. Validation and build commands then operate offline:

On this Mac, the default temporary directory aliases `/var` to `/private/var`.
Four unchanged baseline tests encounter a lexical/resolved path mismatch there.
Use an absolute task-local directory without symlink aliases for `TMPDIR` when
running the suite. With that environment setting, both baseline and candidate
pass all 30 tests; no validator, test or security boundary was changed.

```sh
python tools/validate.py
python -m unittest discover -s tests -v
python tools/build.py
python tools/validate.py --publication
```

The last command must fail closed. Local tests and deterministic generation do not
qualify a host, authenticate evidence, establish runtime containment or authorize
publication. No executable host adapter, live CI, model eval or Xcode run exists.

## Publication and review boundaries

The candidate remains local with no remote configured. Independently review the exact
diff and candidate content before any GitHub creation or push. Resolve maintainer
ownership, private vulnerability reporting, contribution handling and a source-only
release policy. Implement comprehensive SPDX/license validation and trusted producer,
integrity, expiry and revocation checks before qualification or release claims.
The existing publication gate remains an unconditional rejection and cannot be
bypassed by selecting a name or passing tests.

The eight issue texts are drafts only. CI activation is a separate reviewed and
authorized change described in docs/ci-proposal.md. No secrets, credentials, private
application details, unrelated projects or cancelled studio services belong here.
