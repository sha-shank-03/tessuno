# Issue 4 slice: cited Xcode build diagnosis

Tracking issue: https://github.com/sha-shank-03/tessuno/issues/4
This is a practical log-only reference workflow: native Skill, bounded Agent, flat Recipe,
original synthetic build logs, structured response examples and a deterministic scorer.
It is independent of the unmerged adapter-export PR. The existing iOS Studio Pack is
unchanged; this workflow can be inspected separately without claiming Pack qualification.

## Reproduce without Xcode, a model or credentials

Set up the locked Python environment as in tessuno-preparation.md, then run from repository root:

```sh
python tools/validate.py
python tools/evaluate_build_diagnosis.py --examples
python tools/evaluate_build_diagnosis.py --case unresolved-symbol --diagnosis skills/xcode-build-diagnosis/examples/unresolved-symbol.json
python -m unittest discover -s tests -v
python tools/build.py
```

Each authored example passes seven predeclared assertions. These results demonstrate scorer
behavior against manually authored fixtures, not that a model diagnosed them or that Xcode ran.
To check a different answer to a fixture, save sanitized JSON in ignored `scratch/diagnosis.json`
and pass that repository-relative path with --case. Scoring exits 1 for a wrong answer or
invalid closed response; it does not apply fixes. JSON output preserves failed/blocked checks.
Keep temporary test directories outside source. Do not store private app logs, identifiers or
credentials here; `scratch/` is ignored convenience, not a confidential storage guarantee.

## Inputs and useful outputs

| Original synthetic case | Observed diagnostic | Bounded next step |
| --- | --- | --- |
| unresolved-symbol | exact Sources/Settings.swift unresolved-name line | inspect supplied symbol definitions; a suggested name is unconfirmed |
| missing-module | exact Sources/Preview.swift missing-module line | inspect supplied target/dependency configuration; do not install a package |
| incomplete-log | failure wrapper lacks a compiler cause | request compiler log and toolchain context; do not guess or rebuild automatically |

Logs live in skills/xcode-build-diagnosis/fixtures; case contexts/oracles are in cases; authored
answers are in skills/xcode-build-diagnosis/examples. The missing-module log contains an
original hostile instruction asking for deletion and a fabricated success claim. Treat it
as data. Every fixture explicitly says no compiler was run; none was copied from a real app.

Use Skill core/xcode-build-diagnosis v0.1.0 to inspect supplied sanitized lines. The Agent
core/xcode-build-diagnostician reviews citations and gaps. Recipe core/xcode-build-diagnosis-review
separates diagnosis from review and a human checkpoint. The response schema allows only
observations with exact line quotes, unconfirmed hypotheses, bounded proposed action codes,
missing-input codes and explicit not-run/not-applied statuses. No raw command field exists.
For arbitrary real logs the shape is reusable, but these three fixture oracles cannot score
an unknown case. Unsupported diagnostic families require human review and more context.

## Objective acceptance and honest limits

The seven checks are closed response shape (including execution honesty), exact case ID,
exact line citations, complete expected diagnostic set, allowed unconfirmed hypotheses tied
to diagnostic lines, required/allowed next steps, and required missing context. Schema failure
blocks later checks instead of pretending they ran. Complete diagnostics and citations matter;
finding the trailing BUILD FAILED alone cannot pass a compiler-error case. Alternative
predeclared unresolved-symbol hypotheses are permitted; free-form narrative is outside this
small machine-scored shape and must receive separate human review.

Accept this slice only if native/canonical validation, positive examples, hostile/incorrect
responses, ambiguous-case abstention, duplicate JSON, symlink/traversal/ref rejection,
deterministic scores/builds and unchanged qualified-publication rejection pass. Reports bind
case/log/schema/scorer bytes and canonical response digest. Mutable repository oracles and
this local scorer are not a protected trusted evaluation harness; hashes do not authenticate them.
The finite taxonomy/rubric does not establish general diagnostic correctness or model quality.

## Apple capability handoff, not automatic execution

Apple's archived [command-line Xcode FAQ](https://developer.apple.com/library/archive/technotes/tn2339/_index.html)
documents project/scheme listing and build/test operations. Use those established capabilities
in a future separately approved Mac scope rather than a custom execution runtime. Before any
real invocation, inspect the installed version/help, project configuration, dependency-resolution
side effects and isolated output location. Do not infer current flags or compatibility from an
archived document. This reference does not import Apple sample code or an Apple Skill.

A human may separately authorize sanitized project/scheme information or a bounded simulator
build/test with signing disabled and controlled outputs, network and dependency setup. The
log-only objects grant no shell/write/network authority. No toolchain selection/install, signing,
Apple account access, device install, destructive cache cleanup, automatic source/config repair,
archive/export, app publication or credentials are part of this workflow.

Issue 4 remains open: executable original iOS fixtures, version-pinned actual Xcode runs,
seeded executable regressions, predeclared model attempts/assertions and independent role
evaluation remain future work. No Xcode/model/device/account operation ran in this slice.
