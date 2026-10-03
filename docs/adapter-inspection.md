# Issue 3 slice: offline adapter inspection export

Tracking issue: https://github.com/sha-shank-03/tessuno/issues/3
This implements the documentation-only loss-report/export portion, not host qualification.
The exporter emits inert JSON on stdout for inspection and performs no instruction execution,
installation, host configuration, network call or credential access.

```sh
python tools/export_adapter.py --agent core/ios-quality-reviewer --host codex
python tools/export_adapter.py --agent core/ios-quality-reviewer --executable
```

The first command validates the whole catalog and exports exact subject/dependency closure,
license lock, declared permissions and the existing loss report. The second exits 1 with no
JSON output, explicitly listing unsupported filesystem, network and human-approval controls.
No host configuration or executable adapter file is generated. Caller shell redirection, if
used, is the caller's file write; no adapter file is written. Normal Python imports
may create ignored `__pycache__` files; these are not host configuration or Agent exports.

## Acceptance criteria for this slice

- Exact Agent IDs only; reject unknown IDs, non-Agent objects and unsupported hosts.
- Reject closed-schema violations, invalid native Skill dependencies, invalid scope/tool
  declarations, duplicate JSON keys, unresolved references and symlinked resources before output.
- Stable canonical JSON for identical input; content/license changes invalidate the subject.
- Bind running exporter/validator source bytes, consumed schemas and dependency lock separately
  from the object closure. Changed generator bytes invalidate its revision. Hashes do not
  authenticate the generator or prove that installed dependency bytes match the lock.
- Preserve every declared scope/tool/approval requirement and list mandatory controls as
  unsupported. Executable export always rejects, including any forged qualification assertion.
- Leave host version null/unobserved and runtimeQualified false. No environment inspection,
  host launch, permission change, execution authority or trusted-evidence claim.
- Full existing suite, hostile-input fixtures, reproducible build and unchanged qualified-release
  rejection pass. Keep public main and Actions configuration unchanged pending independent review.

## Host documentation and remaining qualification

The current official [Agent approvals & security documentation](https://learn.chatgpt.com/docs/agent-approvals-security)
distinguishes sandbox restrictions, approvals and network controls. Documentation is a reference,
not evidence that this exporter enforces any of them. No mapping to host settings is implemented.
The local Codex CLI was unavailable during development, so no client version or smoke test is
invented. The report deliberately has no caller-supplied host-version or qualification override.

To finish issue 3, select and pin an actual client version and protected harness, then separately
test positive and negative scope/network/approval cases in an approved isolated host environment.
Preserve all attempts and losses; qualify/trust_evidence/publication_gate remain unconditional
rejections. This inspection slice does not close issue 3 or qualify an executable Agent.
