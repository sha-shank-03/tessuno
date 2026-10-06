# Provenance and third-party boundary

All example instructions, fixtures, UI and implementation in this scaffold were authored for
this prototype. No third-party Skills, Apple-exported Skills, application source, binaries or
private logs are bundled. The canonical Agent/evidence contracts implement the owner's revised
foundation proposal. JSON Schema Draft 2020-12 and Agent Skills conventions inform the format.

The validation environment uses jsonschema 4.26.0 and PyYAML 6.0.3, neither vendored. Consult the installed
package's own license when distributing it; this project does not relicense dependencies.
The source checkout includes a repository-only factual inventory at
docs/dependency-license-inventory.md for all seven locked development dependencies.
Verbatim license texts under docs/dependency-licenses/ retain their originating
notices and licenses; they are documentation copies, not Apache-2.0 original work.
Dependency implementations and binaries remain unvendored. The offline kit does not
include this inventory or the license copies. This inventory does not establish
complete compiled-transitive attribution, legal compatibility or admission authority.
Official specification references:
- https://json-schema.org/draft/2020-12/json-schema-core
- https://agentskills.io/specification

The owner selected Apache-2.0 for original scaffold code, documentation and synthetic examples
on 2026-10-02. Per-component SPDX license metadata is Apache-2.0; the complete official text is
in LICENSE. This does not relicense third-party dependencies, specifications, or unrelated content.
No corporate copyright owner or contributor identity is invented. Existing attribution is retained.
Official license source: https://www.apache.org/licenses/LICENSE-2.0.txt
