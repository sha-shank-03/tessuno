# Compatibility

Codex: declared candidate only. Claude Code, Cursor and Gemini CLI: no implemented adapter.
No executable adapter files are generated. The loss report lists filesystem scope, network scope,
and human approval gates as unsupported; tool mapping is unqualified. `qualify` always rejects,
including a forged report declaring success. Empty mandatory controls fail schema validation.

A future Codex-first adapter must use current verified host documentation and pin the actual
client version. Generation tests must remain separate from runtime tests. Every filesystem path,
network destination and approval action needs demonstrated host/isolated-runner enforcement.
A prompt-only instruction is not a gate; partial/unknown support is non-qualified documentation.

No Xcode installation, build, simulator, device, Apple account, MCP access or API key was used.
The fixture build diagnostic is an original static example; no compiler generated it. The regression
fixture includes a failure and not-run case deliberately. Tests check the fixture's expected summary,
not an actual model's ability to diagnose, plan or review. Real iOS qualification remains a separate task.
