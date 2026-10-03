# Trust and evidence

Evidence categories are structure, security, compatibility, execution, enforcement and human-review.
Each has a closed payload. Machine categories require a CI-shaped producer, human review a human-
shaped producer; this validates syntax only. All fixture producers and URLs are explicitly synthetic.
`trust_evidence` rejects every record because provenance verification is not implemented.

Semantic checks reject stale subjects, mismatched candidate/scope digests, duplicate attempts,
inconsistent assertions, incomplete predeclared attempts, duplicate compatibility cases and expired
suppressions. Callers must provide expected subject/scope/attempts for those comparisons; omission
only permits structural inspection, never trust. `publication_gate` always rejects so missing checks
cannot permit release. Suppression checking accepts an explicit UTC clock for reproducible tests.

Pass invariants: structure has no findings; security no findings means only that named scan's result;
compatibility requires all listed cases pass; enforcement requires all three controls fully enforced;
execution requires nonempty passing attempts, nonzero assertions and exact passed/executed equality;
human review must approve the exact candidate and current action scope. Preserve all failed attempts.

An eventual trusted verifier must authenticate producer/workflow, establish artifact integrity,
redaction review, predeclared complete attempts/assertions, host/model/toolchain versions, expiry and
revocation. It must consume protected configuration, never contributor-authored acceptance policy.
No live broker, custom runtime, universal score or self-awarded verified label is part of v0.
