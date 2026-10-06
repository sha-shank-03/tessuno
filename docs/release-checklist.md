# Source usability and remaining release checklist

Recorded 2026-10-05 against main `ca73764a66db6164060313f55c0c441b7ef000c0`,
tree `83cda15e1fc4dc3ed633de0d0a52b36c84e494bd`. PR20–23 are merged. That source
tree passed 133 offline tests, zero skips, in producer and independent review;
five authored diagnosis answers passed 35/35 assertions. Those are source checks.
PR24's workflow-kit source tree `fba48010f0d2cfd481673101e7b1f44ca36e99ce`
passed 139 offline tests in producer and independent review. The maintainer and
project-policy follow-up needs its own exact-head test and review receipt.

## Useful source workflow

| Area | Required observation | Current scope |
| --- | --- | --- |
| Catalog to first task | Open the start page, inspect the original example, follow the exact object/source links and return | Static links; no host activation |
| Download to validation | Extract into a fresh directory and run the documented validator with existing locked dependencies | Archive tests must check the extracted kit, not only the checkout |
| Diagnosis and evidence examples | Run the shipped scorers; preserve zero model/Xcode invocation and BLOCKED release output | Original authored inputs, not real app or model evaluations |
| Content integrity | Match every archive entry to its inventory and every object closure to original bytes; reproduce ZIP bytes | Hashes identify bytes and do not authenticate source |
| Invalid or unsafe inputs | Missing support files, symlinks and modified/unowned generated outputs reject | Stable-snapshot checks; concurrent hostile mutation is outside containment |
| Install expectations | First-run guide lists included tools and omissions; no installer or executable adapter exists | Selected opt-in source inspectors only |

## Browser acceptance

The predecessor catalog-navigation source `94258b8b` / tree `da91956f` was observed
in Codex In-app Browser at 1280x720, 375x812 and 320x568. Later installed-Chrome
checks covered keyboard/reset, links, three history rounds, restored filters/count,
empty results and 320px rendering. Recorded console warnings/errors were zero.
The reviewer inspected the producer's records; they did not independently
reproduce or authenticate those browser actions. That evidence belongs to the
predecessor and does not prove the new start-page workflow.

For PR24's workflow-kit change, reviewed tree
`fba48010f0d2cfd481673101e7b1f44ca36e99ce` / remote head `010a5f0f`, the producer
observed the catalog, start page and native source viewer in installed Chrome
154.0.8037.93, headless, at 1280x720, 375x812 and
320x568. All nine rendered views contained the expected content with no document
horizontal overflow. Chrome handled CDP-generated Tab/Enter on the first catalog
link, pointer navigation from the example through its object backlink and a ZIP
download whose bytes matched the generated archive. All 17 start-page links had
HTTP 200 byte readbacks. Page console warnings/errors were zero; Chrome process
stderr diagnostics are separate and retained in the receipt. The unavailable
agent-browser CLI was replaced by installed Chrome CDP with a temporary profile;
no dependency was installed or shared profile changed.

The maintainer/project-policy follow-up has no new browser observations; changed
metadata, generated viewers and ZIP bytes require their own current-head browser
receipt before claiming that coverage. PR24's exact source/build identities,
screenshots and all attempts belong in its receipt. Keep automated HTML/DOM checks distinct from these producer browser
observations. Independent inspection of the records does not independently
reproduce or authenticate the browser actions. Native OS keyboard traversal, a
screen reader and genuine navigation abort remain NOT_RUN. The old Escape
attempt completed navigation and did not establish an abort. BFCache residency
was not observed. Browser acceptance is not trusted runtime qualification.

## Production and qualification gates

| Gate | Code or recorded evidence | Remaining requirement |
| --- | --- | --- |
| Executable host qualification: BLOCKED | `tools/library.py:qualify` always rejects, including forged success reports | Exact observed host/toolchain versions and isolated positive/negative enforcement tests |
| Filesystem/network/approval controls: UNSUPPORTED | Adapter and native-Skill reports retain declarations and list losses | Demonstrated enforcement of each declared path, destination and approval action |
| Evidence trust: BLOCKED | `trust_evidence` rejects all structurally valid records; capture inventories are unauthenticated | Authenticated producer/workflow, protected policy, artifact integrity, redaction, all attempts, expiry/revocation |
| Qualified publication: BLOCKED | `publication_gate` unconditionally rejects; `validate.py --publication` must exit 1 | Reviewed release policy, identity/license acceptance and trusted qualification; no warning-only shortcut |
| Canonical identity/license inventory: INCOMPLETE | All ten component maintainer declarations match the selected public account/profile; opt-in `validate.py --project-policy` checks those declarations, Apache-2.0 metadata and approved LICENSE bytes | Account/contact authentication, comprehensive SPDX expressions and dependency/per-file attribution policy remain unresolved; no badge is awarded |
| Private reporting route: UNVERIFIED | `SECURITY.md` advertises no verified private route | Readback and monitored delivery evidence before claiming a route; no fabricated mailbox |
| Untrusted CI Lane B: DISABLED | `docs/ci-proposal.md` records unresolved offline runner/isolation boundaries | Independently reviewed isolation/dependency/protected-harness controls before activation |
| Current-source hosted CI: NOT_RUN | Historical Lane A runs bind earlier exact source; manual controller still pins `ade193be` | Separately scoped authorization and exact-source readbacks for any future dispatch |
| Model/Xcode/app release performance: NOT_EVALUATED | Authored examples and inventory checks invoke no model, compiler, device or account | Separately approved genuine evaluation with truthful all-attempt evidence |

The kit and catalog do not change any gate, credential, repository protection or
deployment setting. A completed source checklist permits source inspection and
review; it never admits a production release. No deployment or paid CI follows
from this document or a ZIP download.
