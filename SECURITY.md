# Tessuno security boundary

Tessuno is an inspectable development source scaffold, not a security product or certification.
Repository owner `sha-shank-03` is the security triage owner. No response time is guaranteed.

Native GitHub private vulnerability reporting is planned for the intended repository. Its
enablement, receiver configuration and notification behavior have not yet been verified.
No reporting URL or monitored delivery is claimed. This document will link the native route
only after settings readback; delivery claims require separate notification verification.
Until a private route is verified, retain sensitive findings privately. Do not disclose
vulnerabilities, exploit details, credentials, private evidence or secrets in public issues,
pull requests, discussions or comments. Non-sensitive documentation corrections may use
the ordinary contribution process; remove all confidential material before sharing them.

Assume manifests, instructions, dependencies, fixture setup, graders and build configuration are
hostile. Do not run them with credentials, a host home directory, Docker socket, production data,
write-scoped tokens or network by default. Source inspection does not establish behavioral safety.
The current tools parse data and generate escaped static output; they never execute object instructions.
JSON Schema shape checks do not establish containment or producer authenticity.

Keep evidence private until disclosure is separately authorized and redaction reviewed. Preserve
historical failures/advisories and mark current entries quarantined or revoked when needed. A newer
release does not erase an advisory. No automated revocation service exists in this scaffold.
Public source availability does not establish runtime containment, authenticated evidence,
trusted producer identity or executable qualification. These missing capabilities remain
qualified-release gates; they do not imply that inspectable source must remain private.
