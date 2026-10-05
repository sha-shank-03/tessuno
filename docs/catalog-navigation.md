# Inspect an object and return from its source

Build the offline catalog with `python tools/build.py`. Each object displays its exact
ID as a link, using a stable `index.html#object-<ID>` fragment (the ID is URL encoded
in generated links). The fragment identifies the object, not an immutable version or
content digest; compare the separately displayed version and exact digest when
reviewing different builds.

Contract-source links are visible without opening the dependency list. Skills also
link directly to their native SKILL.md bytes. Every source viewer lists the catalog
objects whose exact dependency closure includes that file. Shared dependencies and
license files can belong to several objects; the backlinks do not imply execution,
installation, enforcement or qualification.

All links and source text work without JavaScript. When scripts are available,
opening a known object fragment clears search/type/stack filters, shows all objects,
and focuses and scrolls to the selected object. An unknown or malformed fragment
leaves the filters unchanged. This prevents source backlinks and browser history
from landing on an object hidden by a previous filter. Object cards are focus targets
but are not added to the normal Tab order.

Automated checks cover exact closure membership, URL/readback escaping, original
bytes, deterministic outputs and mocked DOM fragment/filter behavior. Mocked DOM
checks do not establish browser rendering, native keyboard behavior, scroll position
or accessibility acceptance. Those still require an approved browser preview.
