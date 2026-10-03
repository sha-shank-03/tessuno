# Independent checkpoint review

## Checkpoint 81c6f6c497b75202e334980fddede67d933a6da5

The initial 21 offline test methods passed. Independent adversarial review then reproduced
failures that those tests missed. They remain recorded here rather than being erased by a green rerun:

1. Native frontmatter accepted booleans, null, numbers, comment-only, empty quoted and malformed
   quoted descriptions. Fix: safe YAML parsing with duplicate-key rejection, exact supported keys,
   actual nonempty string types, native name constraints and nonempty body.
2. Removed source resources remained in dist/source after rebuilding and were omitted from new
   checksums. Fix: verify the previous generated receipt, preserve unknown/modified files by failing,
   and remove only unchanged previously generated resources no longer part of the current output.
3. A resource containing # generated a broken fragment URL. Fix: encode source URL paths while
   preserving source text and filesystem names; add link-resolution regression tests.
4. A schema symlink could cause build output to contain synthetic outside-repository bytes; the
   validator also accepted it. Fix: reject symlinks and nonregular inputs across schemas, static
   assets, manifests and resources before reads/archive inclusion, including directory components.
   Auxiliary resource symlinks now fail validation, not merely generation. Nonlocal schema $ref
   retrieval is prohibited to keep validation offline.

The review used isolated synthetic files; no private content was accessed. Regression tests now
cover all four defects, safe preservation of user-edited output, and nonlocal schema references.
A subsequent self-check also found the generated checksums receipt was read before the output
symlink walk. It now receives safe-path validation before reading, with a dedicated regression.
A second independent pass found that remote $dynamicRef values were not yet rejected. The
central schema reader now guards $ref, $dynamicRef and $recursiveRef for catalog and direct record
validation; regression cases cover each keyword in common, Agent and evidence schemas.
The revised suite has 27 methods plus parameterized cases. Independent final recheck is pending.

## Verification limits

A cloud-browser attempt to inspect localhost was blocked by ERR_BLOCKED_BY_CLIENT. No workaround
was attempted. HTML links, output bytes and reproducibility were checked offline; visual/browser
interaction QA has not run. No Xcode, host adapter, model evaluation or GitHub execution occurred.
No trusted evidence producer verification or public release authorization exists.

## License update, 2026-10-02

The owner selected Apache-2.0 for original scaffold work. The clean Git baseline was verified
at 7ab91962d2790a8ccba90b321dc075125ed628ba; original Git history remained available, so recovery
or history reconstruction was unnecessary. The official Apache license text was downloaded
unchanged, and its SHA-256 is recorded in docs/licensing-decision.md. No copyright-owner identity,
corporation, DCO or CLA was invented. Third-party boundaries and attribution are retained.

Object/fixture license metadata, documentation, generated catalog and archive license contents
were updated. Applicable license and notice bytes now participate in candidate digests. New tests
check official license bytes, object/fixture metadata, archive/catalog readback and invalidation
after an attribution change. Containment tests include the new root license inputs.
Publication and executable qualification continue to refuse; selecting a license does not resolve
identity, trusted evidence, host execution or publishing authorization. Independent review of the
license-only checkpoint is required before replacement delivery.
