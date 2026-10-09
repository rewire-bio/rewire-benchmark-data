# Use-case evidence re-pin, 2026-10-09

The issue #42 migrations (controlled vocabularies, single-meaning relations and the vocabulary follow-up corrections, each with its own review in this folder) rewrote records that reviewed use-case mappings depend on. Each mapping pins a fingerprint of those records' bytes, so the release after the migrations withheld 92 mappings the live website serves, and the website refused to adopt it.

At the maintainer's direction, every active mapping is re-pinned to the current records with `npm run use-cases:repin`. The fingerprints are accepted as reviewed through the migration reviews; the mappings themselves were not re-read. The fingerprint system is due to be replaced in a separate change.
