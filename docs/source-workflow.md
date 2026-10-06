# Start with an offline source workflow

The catalog's `prototype.zip` download is an inspection kit: original Agent, Skill,
Recipe and Pack source, exact dependency manifests, schemas, license notices, a
dependency lock and selected offline inspectors. Extract it into a new directory
and work there. Nothing in the kit installs a Skill, writes host configuration,
launches an Agent, calls a model or grants execution authority.

## 1. Check the contents and prerequisites

Read `LICENSE`, `THIRD_PARTY_NOTICES.md` and `inspection-kit.json`. The inventory
lists every other archive file and its SHA256. Compare bytes if needed; hashes
identify content and do not authenticate its author or establish safety.
`content-manifests.json` preserves each object's exact version, transitive source
closure, license lock and unsupported adapter controls. Keep `SKILL.md`, its
`library.json` sidecar and resources together when inspecting a Skill.

Use Python 3.11+ in an existing isolated development environment with
jsonschema 4.26.0 and PyYAML 6.0.3. `requirements-dev.lock` retains all seven
development dependencies and platform wheel hashes from the repository. The kit
does not create an environment, install dependencies or download packages. If
setup is needed, consult the repository's `docs/tessuno-preparation.md` before
choosing a separate setup action. That setup guide and the full repository test
suite are not part of this bounded kit.

From the extracted directory:

```sh
python -B tools/validate.py
```

Success checks ten source objects and their exact references. It establishes local
schema/semantic validity, not host compatibility, security or trusted evidence.

## 2. Choose an outcome

**Plan a change.** Read `skills/ios-test-plan/SKILL.md` and the original
`skills/ios-test-plan/examples/toggle.md` input. Follow the instructions manually
to prepare acceptance, failure and accessibility cases from the supplied
description. Keep proposed tests labeled NOT RUN and preserve missing inputs.
Use the Agent and Recipe contracts to inspect a proposed handoff; they do not run
that handoff. This is a useful planning procedure without installing anything.

**Understand a build diagnostic.** Inspect the original log and authored response
under `skills/xcode-build-diagnosis/fixtures/` and `examples/`. Then compare all
five authored responses with their expected outcomes:

```sh
python -B tools/evaluate_build_diagnosis.py --examples
```

The 35 assertions check exact citations and response structure. A pass means the
authored response matches its case. It measures neither a compiler run nor a
model's ability to diagnose a real build; no fix is applied.

**List release-evidence gaps.** Read
`skills/release-readiness-evidence/SKILL.md`, then inspect the complete original
packet or its missing/failure variants:

```sh
python -B tools/evaluate_release_packet.py skills/release-readiness-evidence/fixtures/complete.json
```

Even the complete packet reports release BLOCKED, trustedEvidence=false and
runtimeInvoked=false. Use the procedure to identify the next evidence collection
task; an authored inventory never authorizes release or account actions.

## 3. Review compatibility before considering a host

```sh
python -B tools/inspect_skill_portability.py --skill core/ios-test-plan
python -B tools/export_adapter.py --agent core/ios-quality-reviewer
```

Reports preserve native bytes and declared permissions while listing losses.
Host versions are unobserved. Filesystem scope, network scope and human approval
enforcement remain unsupported. A prompt instruction or suggested discovery path
does not enforce those controls. The kit contains no installer or executable
adapter; `--executable` requests reject.

## 4. Keep source acceptance separate from release

```sh
python -B tools/validate.py --publication
```

This must exit 1. See `docs/release-checklist.md` for the current source, browser,
host and provenance gaps. Do not erase missing observations or convert these
offline results into runtime, model, security or human-approval badges.

The selected Python tools run only when explicitly invoked by the reader. The kit
is not the full development checkout: it omits the builder, CI controller, Xcode
runner and test suite. Use the repository for development and independently
review any changed snapshot before relying on its source checks.
