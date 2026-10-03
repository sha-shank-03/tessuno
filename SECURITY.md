# Security boundary

This prototype is private and is not a security product or safety certification.
No public reporting mailbox has been established. Report concerns privately to the project owner
in the same authorized conversation; do not create a public issue containing sensitive details.
A real private reporting route, response ownership and revocation process are launch blockers.

Assume manifests, instructions, dependencies, fixture setup, graders and build configuration are
hostile. Do not run them with credentials, a host home directory, Docker socket, production data,
write-scoped tokens or network by default. Source inspection does not establish behavioral safety.
The current tools parse data and generate escaped static output; they never execute object instructions.
JSON Schema shape checks do not establish containment or producer authenticity.

Keep evidence private until disclosure is separately authorized and redaction reviewed. Preserve
historical failures/advisories and mark current entries quarantined or revoked when needed. A newer
release does not erase an advisory. No automated revocation service exists in this prototype.
