# Architecture

Source → closed schemas and semantic validation → exact dependency closure → deterministic
content manifests/locks → inert archive and static inspection catalog. No execution engine exists.

Agents describe bounded roles. Skills preserve native SKILL.md with a JSON sidecar. Recipes are
ordered steps with exact Agent/Skill references and optional human checkpoints. Packs contain exact
Agent/Skill/Recipe versions, with no nested Packs. Object IDs are unique within the repository.

schemaVersion is exactly "1"; object version is independent strict three-part semver (no ranges).
Unknown fields and versions are rejected. The Agent/evidence contracts preserve the independently
reviewed foundation's standalone closed records; common.schema.json documents common primitives
without fragile allOf/additionalProperties inheritance. Any contract change needs negative tests.

The content digest covers sorted normalized file-byte digests for the transitive object/resource
closure, content-addressed source revision, exact component versions, adapter-loss report and lock.
Applicable root LICENSE and third-party-notice bytes are included in every candidate digest.
Evidence envelopes remain outside that digest. Build output is reproducible, has no clock stamps,
uses fixed ZIP timestamps/modes and sorted entries. Git identity is separate from content identity.

The catalog displays raw metadata, dependency source and content digest. It imports no evidence
records and cannot award a tested/verified badge. All source is escaped; source downloads use .txt.
Local checks are structure/semantics, not a trusted scanner, model eval or runtime qualification.

All consumed inputs use repository-relative regular-file checks; symlinks in path components,
including schema and asset directories, are rejected. These checks are offline validation, not
an OS containment mechanism. Concurrent hostile filesystem mutation (TOCTOU) is not prevented;
run on an immutable isolated candidate snapshot for security-relevant verification. The current
local build assumes source files are not changed concurrently. Adapter report digests bind report
bytes; any future executable adapter must separately bind trusted generator/harness revisions.

Build cleanup only removes unchanged prior-generated files recorded in the previous checksums
receipt. Unknown files or modified generated files cause failure and are preserved. A interrupted
build may require manual reconciliation; it never treats modified output as automatically disposable.
