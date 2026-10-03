# Proposed issue: Browse the development catalog by object type and stack

No matching dedicated issue exists among public issues 1–8 as read on 2026-10-03.
This is a proposed standalone catalog issue, not an expansion of issue 4. No remote
issue was created. Candidate starts from public main f19a87ab6d1a390f0c1848b2338b21301163494e
and depends on none of draft PRs 9–11.

Scope: Add metadata-derived type and stack selectors to the existing generated static
catalog. Combine exact selectors with existing case-insensitive, all-token text search.
Keep source inspection and declared-only/evidence limitations visible. No database,
hosting, telemetry, dependency acquisition, runtime execution or CI activation.

Acceptance criteria:

- Type/stack options and per-card values come from validated catalog records.
- Text search and both filters intersect; stack uses exact membership.
- A live count shows matching/total objects; zero results explain recovery.
- Clear resets all controls and returns focus to search.
- Native labeled controls, visible keyboard focus and a single-column narrow layout.
- All objects/source links remain readable without JavaScript; inactive controls are disabled.
- Existing evidence caveats and direct contract/source inspection are retained.
- Deterministic build and positive/negative tests pass; browser checks cover empty state,
  keyboard traversal, narrow viewport and source navigation before UI acceptance.

The local candidate has automated metadata/readback and mocked DOM behavior checks.
The mock is not a browser or accessibility test. Native keyboard behavior, rendering,
viewport overflow and screenshots remain unverified because the sandbox denied a
loopback server bind and the browser URL policy rejected local file previews. No
permission changes or workaround was attempted. Independent review and an approved
preview environment remain required before publication/visual acceptance.
