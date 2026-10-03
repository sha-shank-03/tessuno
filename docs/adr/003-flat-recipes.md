# ADR 003: flat recipes and immutable packs

Accepted: ordered referenced steps, no loops/nested delegation engine; exact Pack members, no
nested Packs. Resolve closure before build. Content-addressed locks prevent silent latest updates.
