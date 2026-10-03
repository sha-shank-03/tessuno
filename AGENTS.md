# Repository development rules

This is the unpublished Tessuno development candidate, based on a reviewed synthetic portable-library prototype. It grants no execution authority.
Keep library objects inert: no installer, runtime, remote calls, provider calls, or secret access.
Use original synthetic fixtures only. Never copy private application code, account identifiers,
bundle identifiers, credentials, host agent configuration, or private test artifacts here.

Before changing contracts read docs/architecture.md and docs/trust-and-evidence.md.
Run `python tools/validate.py`, `python -m unittest discover -s tests -v`, and
`python tools/build.py`. Test negative cases alongside positive cases. Never turn a blocked
release gate into a warning. Original scaffold work is licensed Apache-2.0 by owner decision; preserve LICENSE and notices.
Keep generated output in ignored dist/. Do not push, publish, deploy, or enable CI implicitly.
A generator is not a host test; a schema-valid record is not trusted evidence.

Always ask the owner before production App Store releases, destructive database migrations,
irreversible deletion or infrastructure changes, production secret rotation, Apple ownership
or permission changes, legal agreements, banking/tax actions, material ad spend or significant
pricing changes, deleting production apps, or changing bundle identifiers.
