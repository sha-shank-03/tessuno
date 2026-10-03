# ADR 001: native Skills with closed sidecars

Accepted for private scaffold: retain SKILL.md name/description and original resources. Store
portable metadata in JSON sidecars. Narrow native parsing rejects unsupported frontmatter rather
than silently losing controls. No custom loader or installer is introduced.
