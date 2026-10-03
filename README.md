# Tessuno

Tessuno is an Apache-2.0 foundation for inspectable, reusable Agents, native Agent Skills,
Recipes and Packs. The initial slice is iOS Studio; cross-stack support is a future roadmap.
This v0.1 development candidate is prepared for public open-source collaboration but remains
unpublished. The owner selected Tessuno on 2026-10-03; maintainer and reporting ownership
still require decisions before launch.
Original scaffold code, documentation and synthetic examples are licensed **Apache-2.0**; see LICENSE
and THIRD_PARTY_NOTICES.md. No public repository, publication, installer or executable host adapter exists.

## What works locally

- Four strict Draft 2020-12 JSON contracts: Agent, native Skill sidecar, ordered Recipe, exact Pack
- Typed evidence contracts with category/producer variants, pass invariants and digest checks
- One original iOS review slice: test-planning Skill, independent reviewer Agent, Recipe and Pack
- Deterministic validation, closure hashes, lock/license inventory, static source-inspection catalog,
  inert synthetic archive, and offline positive/negative tests
- Adapter loss reports explicitly refuse executable qualification; no Codex TOML is generated

Compatibility is declared-only. No Codex, Xcode, simulator, device, model, security scanner,
GitHub CI, external producer, or human approval has been qualified by this repository.
Evidence fixtures are synthetic test inputs, never evidence that those checks occurred.

## Run offline

Requires Python 3.11+ and jsonschema 4.26.0 and PyYAML 6.0.3 in an isolated development environment.
The original source environment and this Mac preparation are documented separately in
docs/tessuno-preparation.md; dependency installation is an explicit setup step.
No dependency installation, network call or package download is performed by these commands.

```sh
python tools/validate.py
python -m unittest discover -s tests -v
python tools/build.py
python tools/validate.py --publication  # MUST fail: unresolved release gates
```

Open dist/index.html to inspect the catalog and source. For same-origin script execution,
serve dist with a local-only HTTP server. Do not expose it publicly. The search box filters
kind, stack, platform, origin, declared support, network and write-scope terms. Without scripts,
all objects and plain-text source links remain visible. Two builds produce identical bytes.

## Boundaries

JSON manifests avoid YAML coercion; SKILL.md retains native name/description frontmatter.
The native validator deliberately supports a narrow subset, not all valid Agent Skills YAML.
The original-work license and Tessuno name are selected; maintainer identity is still pending. Publication always
fails closed until a separately reviewed release policy, comprehensive SPDX/license validation, real maintainer,
producer provenance verifier and actual host qualification exist. No data is silently upgraded
to a trust badge. No production app code or identifiers are included.

See docs/architecture.md, docs/compatibility.md, docs/trust-and-evidence.md,
docs/licensing-decision.md and docs/issue-drafts/roadmap.md. Safe CI is a disabled proposal
in docs/ci-proposal.md; no live GitHub workflow or remote issues are created.

See docs/tessuno-preparation.md for source provenance and repository preparation boundaries,
and docs/issue-drafts/tessuno-eight-issues.md for eight bounded proposed GitHub issues.
