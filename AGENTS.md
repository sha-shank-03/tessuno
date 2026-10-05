# Repository development rules

Tessuno is an inspectable development source scaffold, based on a reviewed synthetic
portable-library prototype. The initial prepublication preparation is recorded in
docs/tessuno-preparation.md. Maintainer and triage owner: GitHub account sha-shank-03.
Public repository setup, merged PR 17 source integration and two separately authorized
bounded Lane A runs are recorded in docs/ci-proposal.md. Recorded main `a55e9e6f` has
the same tree as checked source `f0ff1194`; its later run passed 98 tests and preserved
the qualified-publication rejection. These are source checks, not host/runtime qualification.
The controller still pins `ade193be`; do not repoint or dispatch it without separate
authorization. Future edits need independent review; completed runs authorize no rerun.
Private reporting settings remain unverified here.
Public source preview follows docs/source-preview-policy.md and grants no execution authority.
Keep library objects inert: no installer, runtime, remote calls, provider calls, or secret access.
Use original synthetic fixtures only. Never copy private application code, account identifiers,
bundle identifiers, credentials, host agent configuration, or private test artifacts here.

Before changing contracts read docs/architecture.md and docs/trust-and-evidence.md.
Run `python tools/validate.py`, `python -m unittest discover -s tests -v`, and
`python tools/build.py`. Test negative cases alongside positive cases. Never turn a blocked
release gate into a warning. Original scaffold work is licensed Apache-2.0 by owner decision; preserve LICENSE and notices.
Keep generated output in ignored dist/. The owner authorized a new public Apache-2.0 Tessuno
source project and autonomous setup; do not request those settled choices again. Review the
exact future source diff before push and verify settings/content before reporting
publication as complete. Do not implicitly activate CI, deploy, publish packages, create release
tags or qualify agents. Public source availability never changes the fail-closed code gates.
A generator is not a host test; a schema-valid record is not trusted evidence.

Always ask the owner before production App Store releases, destructive database migrations,
irreversible deletion or infrastructure changes, production secret rotation, Apple ownership
or permission changes, legal agreements, banking/tax actions, material ad spend or significant
pricing changes, deleting production apps, or changing bundle identifiers.
