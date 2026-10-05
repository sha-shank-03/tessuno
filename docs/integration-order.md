# Source integration order for drafts 20–23

Recorded on 2026-10-05. These are source-review prerequisites, not merge approval,
CI dispatch, deployment, host execution or release qualification. Refresh this
ledger when an input advances; review and test results bind the checked snapshot.

| Draft | Recorded base | Source input | Branch-local tests |
| --- | --- | --- | --- |
| [20: documentation](https://github.com/sha-shank-03/tessuno/pull/20) | main `a55e9e6f1e3a32882b73e002c5126c71b7706970` | `ad90c20d78755cac12b23c29e41a1f1ee6bc26d2` | 98; documentation-only |
| [21: capture inventory](https://github.com/sha-shank-03/tessuno/pull/21) | draft 20 `ad90c20d78755cac12b23c29e41a1f1ee6bc26d2` | `8516885757da2024c865696dfee02607c0238ccf` | 121 = 98 + 23 capture tests |
| [22: catalog navigation](https://github.com/sha-shank-03/tessuno/pull/22) | main `a55e9e6f1e3a32882b73e002c5126c71b7706970` | `6cb4d48a3052d1e7f32a538078dac2016d147926` | 103 = 98 + 5 navigation tests |
| [23: diagnosis fixtures](https://github.com/sha-shank-03/tessuno/pull/23) | main `a55e9e6f1e3a32882b73e002c5126c71b7706970` | extended revision accompanying this ledger; exact reviewed head/tree in PR body | 105 = 98 + 3 same-family + 4 mixed-family tests |

PR 23 extends its existing draft rather than introducing another branch. Its
predecessor `2d916468f2eac943b144f6c7a6bddc523320aeaa` passed 101 tests; that result
does not cover the mixed-family extension. The seven fixture assertions are
separate from test-method totals: five authored answers have 35 assertions.

Use **20 → 21 → 22 → 23** as the integration sequence. The hard dependency is
20 before 21. After an authorized merge of 20, retarget/reconcile 21 onto the
resulting main while preserving its six-file capture delta. Reconcile 22 and 23
with the resulting main instead of treating their separate totals as regressions.
Expected cumulative totals are 98, 121, 126 and 133 respectively, assuming the
pinned source inputs and no further test changes.

README is shared by 20, 21 and 23: retain 20's historical source-check wording,
21's capture entry and 23's current fixture wording. Do not overwrite the entire
file from one branch. Other pinned changed-file sets are disjoint. A temporary
assembled snapshot checks the full sequence with three-way README reconciliation;
its exact inputs, merge exits and test result are recorded with this draft's
validation artifacts. It is not a merged or separately qualified release.

Before integration, compare current heads/bases and changed-file lists with this
ledger, reconcile any changed input, run validation, the complete test suite,
source hygiene and deterministic builds on the exact combined tree, and retain
the expected publication rejection. Review that final combined diff and record
its tree identity. Any future merge or controller repoint/dispatch requires its
own authorization; historical Lane A results do not validate these newer heads.
Screen-reader and genuine navigation-abort acceptance remain NOT_RUN; source
and browser checks award no trusted runtime or human qualification.
