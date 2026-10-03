# Original compile-only Xcode fixture

This opt-in experiment adds one original Swift arithmetic source, a static-library
project and a shared build scheme. No scripts, packages, application, bundle ID,
signing identity, tests, simulator launch, model or network dependency are included.
It is separate from the authored diagnosis examples and does not change library
permissions, trust gates or qualify an Agent.

Review the exact project, inventory and command builder before execution. On a Mac
with an already configured Xcode and installed iPhone Simulator SDK, the explicit
invocation is `python tools/run_xcode_fixture.py --sdk iphonesimulator27.0 --output
/path/to/new/private/evidence`. Use an absolute destination outside the repository
within existing writable permissions. Do not install tooling, accept terms, modify
accounts or expand permissions to run it. No CI invokes this runner.

The runner verifies the reviewed three-file inventory, records local Xcode version
and SDK listing, then permits at most baseline, seeded unresolved-symbol and restored
builds, each from a fresh source snapshot with separate DerivedData and caches.
Each build has a 120-second bound. It preserves exact command arrays, input hashes,
raw logs, exits and product hashes. Exit zero plus a static archive is required for
success; the seeded failure requires the exact Swift diagnostic. Any explicit
permission denial stops subsequent attempts even if compilation succeeded. Timeout
or another unexpected result also stops; there is no retry or deletion. A timeout
kills the direct process; this is not a process-tree isolation mechanism.

Raw Xcode output can enumerate personal provisioning profile paths even with signing
disabled. Keep receipts/logs private; review and redact before publication. No local
raw log is committed. The diagnostic matching is specific to this original fixture;
this runner is neither a general log evaluator nor trusted runtime evidence.

## Local observation on 2026-10-03

Xcode 27.0 (27A266a), SDK iphonesimulator27.0 (24A430): one baseline build returned
0, reported BUILD SUCCEEDED and produced an unsigned static archive. Nonfatal
FSEvents and cache fallback warnings were followed by a denied CoreSimulator log
write outside the workspace. Further Xcode invocations stopped. Seeded failure and
restored baseline remain unexecuted; no real-error diagnosis case is added. The
recorded baseline predates this runner and used the reviewed source directly rather
than a snapshot. It is a manual observation, not a complete runner pass.

Unit tests exercise the inventory, command constraints and positive/negative result
classification without invoking Xcode. Issue 4 remains open; runtime behavior, model
quality, device behavior and broad toolchain compatibility are untested.
