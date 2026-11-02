# Enchant v3

Requested in issue #229. Enchant v3 is Iambic's multimodal transformer for drug discovery, announced on
21 September 2026. The three Iambic pages named in the issue are the sources. The LinkedIn announcement in the
issue is not a source.

## Decisions

- **Recorded as a service-level model** (`entity_level: service`), like other closed models such as GPT-4o. No
  weights, public API or licence was located, so the model can only be used through Iambic.
- **Status discovered.** The issue asks for a discovered model with a source-linked profile. No performance is claimed.
- **Separate from Enchant v1, v2 and NeuralPLexer.** None of them is in the store. The profile names them only to
  say that their results and terms do not carry over.
- **No results from Figure 7.** The figure prints TM-scores on CAMEO22 (Enchant 0.775, ESM3 0.746, DPLM-2 0.694)
  and CASP14 (0.575, 0.534, 0.500). It does not say which Enchant version, which ESM3 and DPLM-2 configurations,
  which structures were held out, or how scores were averaged. The issue asks for results only when those are
  sourced. The figure is `6aa92e46b4324528eb1612c3_ghost.svg` on the Webflow CDN, SHA-256
  `db7b416f6eda8c8e02f5feca73167f0795714d96cde637af9552b4a43a43a2c9`, with its text drawn as paths.
- **Drug programmes are case studies.** IAM-C1 and IAM217 are recorded as a limitation, not as evaluations.
