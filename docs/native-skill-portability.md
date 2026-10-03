# Native Skill portability inspection

This bounded issue [3](https://github.com/sha-shank-03/tessuno/issues/3) slice compares the
existing native Skill format with documented project discovery conventions for Codex,
Claude Code, Cursor and Gemini CLI. It emits inert canonical JSON to stdout. It inventories
source bytes; it does not copy resources, install Skills, write host configuration, launch a
host, use credentials, call a model or qualify execution. It is independent of PR 9's Agent
closure/permission inspector and does not finish issue 3.

```sh
python tools/inspect_skill_portability.py --skill core/ios-test-plan
python tools/inspect_skill_portability.py --skill core/ios-test-plan --host claude-code
python tools/inspect_skill_portability.py --skill core/ios-test-plan --executable
```

The first two commands emit reports; the third rejects with exit 1, empty stdout and all
three unsupported controls. Exact catalog Skill IDs are required. Agent, Recipe and Pack
IDs, paths, unknown hosts, invalid catalogs and extended native frontmatter reject before
report output. The existing canonical schemas and narrow native validator remain unchanged.
Normal Python imports may create ignored bytecode caches; use `python -B` to avoid them.

## What is preserved and what is lost

The native entry is never reconstructed from sidecar identity, title or purpose. The report
binds each original file's bytes and keeps resource paths relative to the Skill directory.
`library.json` is labeled as the canonical sidecar, distinct from the native entry and
unqualified resources. Inventory is not a copying plan or a resource-resolution test.

Every canonical sidecar field and its exact nested value appears once in `canonicalFields`.
`entry` identifies the native entrypoint. `filesystemScope`, `networkScope` and `requiredTools`
are explicitly unsupported enforcement declarations. All other fields are retained only in
the report with no native mapping. No fields are silently flattened into prose or inserted
into YAML. In particular, canonical license/version metadata is not automatically inserted
into optional native fields. The root license and notices still participate in the subject.

Each host lists filesystem scope, network scope and human approval gates as unsupported,
even for a Skill with no writes or network access. These are inspection checks, not fabricated
`requiredControls` requirements on the canonical Skill contract. `repository.read` remains
unqualified. Prompt instructions, invocation controls, activation consent and discovery paths
do not establish enforcement of the canonical declarations.

## Documentation references

The original reference profiles were reviewed on 2026-10-03. They cover only the existing
`name`/`description` frontmatter subset and project-local discovery, not every supported
host field, cloud mode, plugin, precedence rule or configuration option.

| Host | Documented project roots | Behavioral difference to review |
| --- | --- | --- |
| [Codex](https://learn.chatgpt.com/docs/build-skills) | `.agents/skills` | Explicit or description-based invocation; duplicate names are not merged. |
| [Claude Code](https://code.claude.com/docs/en/skills) | `.claude/skills` | Host extensions include substitutions and dynamic context; some names are reserved. |
| [Cursor](https://cursor.com/docs/skills) | `.agents/skills`, `.cursor/skills` | Context selection and slash invocation have host-specific lifecycles. |
| [Gemini CLI](https://geminicli.com/docs/cli/skills/) | `.agents/skills`, `.gemini/skills` | Activation requests consent; the shared alias wins within its discovery tier. |

The [Agent Skills specification](https://agentskills.io/specification) describes the common
native format and optional fields. Tessuno intentionally supports a narrower subset. Extending
that subset or adding host policy mappings requires a separately reviewed contract proposal.
The report's suggested directories are documentation strings; no filesystem writes occur.

`bodySignals` conservatively identifies Claude-style dynamic context (`!` followed by a
backtick) and argument/session placeholders. Matches in examples or escaped text can be false
positives. Absence of matches proves nothing: this is not an exhaustive parser, security scan
or assertion of equivalent behavior. Text is never interpolated or executed. Documented Claude
reserved names `synced` and `anthropic-skills` produce an explicit discovery-loss entry.

## Binding and limits

The existing subject/manifest/lock binds native source, sidecar, resources and root attribution.
The report separately binds the running inspector, imported validator, every consumed catalog
schema, dependency lock and host-profile bytes. Separate tool/catalog roots retain separate
source labels. `profileDigest` identifies the local reference table. `reportDigest` covers
canonical JSON of all other report fields, including selected hosts and losses.

Host versions remain null/unobserved. URLs and the review date are references, not immutable or
authenticated remote-document snapshots. Generator hashes identify local bytes; they do not
authenticate those bytes or installed dependencies. All native behavior, resource resolution,
tools and runtime qualification remain unqualified. Reports use no clock, Git lookup or host
environment discovery. Inspection assumes a stable source snapshot; existing filesystem
checks do not prevent concurrent hostile mutation.

Offline synthetic tests exercise exact field/resource inventory, broadened permissions,
sidecar and YAML attacks, dynamic-body non-execution, reserved names, symlinks, stale bindings,
separate source roots and zero-output executable rejection. These are generator tests only.
Actual client/harness versions, protected provenance and approved isolated positive/negative
enforcement tests remain necessary for future qualification. Publication and evidence trust
gates continue to reject unconditionally.
