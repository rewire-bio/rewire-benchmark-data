# Layer registry and sanity gate: what the archive actually gives the extractor

ADR 0002 step 4, measured over the archive as it stands on 2026-11-18. Every
number below has the command that produced it. Nothing here is an estimate.

## What was built

| Path | What it is |
| --- | --- |
| `shared/omics/layers/types.ts` | The record contract: one layer, its identity, its metrics, its verdict |
| `shared/omics/layers/sanity.ts` | The gate, with every threshold set from the measured distribution |
| `shared/omics/layers/registry.ts` | Generation from the object manifest, and reading the generated files |
| `shared/omics/layers/coverage.ts` | The per-source buckets and the arithmetic identity |
| `shared/omics/layers/index.ts` | The interface another lane calls |
| `scripts/omics/layers/cli.ts` | `npm run layers -- build \| check \| coverage \| surface \| show` |
| `data/omics/layers/registry.jsonl` | Generated. 2,301 rows, 2,021,690 bytes |
| `data/omics/layers/unsupported.jsonl` | Generated. 245 held nodes that produce no layer, each with the reason |
| `tests/omics-layer-registry.test.ts` | 20 tests |

The derivation is `shared/archive/layers`, which the archive lane owns and
which this calls. No manifest row was written, no object was stored, and the
registry holds no layer bytes: it is a projection of the manifest, and a
layer's bytes stay in the one store ADR 0004 defines.

## The registry

`npm run layers -- build`

| | |
| --- | --- |
| Objects read | 1,167 |
| Layers | 2,301, over 2,122 distinct layer hashes |
| Of those, container members | 1,168 |
| Identity layers, where the object already is its own text layer | 1,569 |
| Nodes that produce no layer | 245, inside 25 objects |
| Objects that produce no layer at all | 2 of 1,167 |

| Normaliser | Layers | Characters |
| --- | --- | --- |
| `text-utf8@1` | 1,569 | 34,048,822 |
| `ooxml-sheet-tsv@1` | 65 | 66,999,115 |
| `pdf-text-layer@1` | 201 | 22,668,939 |
| `europepmc-fulltext-xml@1` | 259 | 16,749,148 |
| `html-text@1` | 198 | 4,134,295 |
| `ooxml-document-text@1` | 9 | 108,857 |

Regeneration is a no-op. `npm run layers -- check` re-derives all 1,167
objects from the stored bytes and reports `2301 layers reproduce`, meaning the
committed file is byte for byte what the store produces. Two independent full
derivations also gave the same 2,301 layer hashes, pdftotext 26.08.0 included,
which is the evidence that a span taken today still points at the same
characters tomorrow.

## The sanity gate, and where each threshold came from

The calibration set is the 2,301 layers. 24 of the 1,167 objects are labelled
bad by the archive lane: their latest fetch receipt says `not_artifact`. The
rule everywhere is that a `fail` threshold cuts none of the real work, because
a gate that refuses real work gets switched off. That is how the one check
this repository already had came to be run on 14 of 194 batch folders.

| Property | Rule | Measured distribution | What the rule cuts |
| --- | --- | --- | --- |
| Offsets stable under regeneration | the layer re-derives to the same sha256 | 2,301 of 2,301 identical across two runs | 0 |
| Non-zero characters | at least one non-whitespace code point | 8 layers of 2,301 hold none: 6 HTML pages that render to nothing, 2 PDFs whose layer is three page breaks | 8 (0.35%) |
| Printable ratio | fail under 0.98, suspect under 0.999 | minimum over the 2,295 layers with content is 0.9914, on the Chai-1 technical report, whose layer carries 400 control characters in 46,500, 306 of them NUL | fail 0, suspect 2 (0.09%) |
| U+FFFD | fail over 0.01 of the layer, suspect on any | 11 layers carry any, highest share 0.0030 | fail 0, suspect 11 (0.48%) |
| Punctuation-run mojibake | fail when punctuation is over 0.25 of the layer and digits under 0.005 of its alphanumerics, on 1,000 characters or more | over the 1,915 layers at or above 1,000 characters: 15 carry punctuation above 0.25, with digit shares from 0.044 to 0.879; 157 carry a digit share under 0.005, and the highest punctuation share among those is 0.1661; the two together occur 0 times | 0 |
| Page breaks against pdfinfo | equality, no tolerance | all 201 PDF layers agree with pdfinfo, 201 of 201 | 0 |

Verdicts over the store: 2,280 pass, 13 suspect, 8 fail.

The mojibake rule is the one ADR 0002 names by example: bacformer version 2
rendered 0.81 +/- 0.07 as `+.)! +.+(` and a conclusion was drawn from it. That
layer is not in the archive, so the rule is asserted against the documented
rendering in `tests/omics-layer-registry.test.ts`. Version 3 is in the archive,
at layer `86636e89b167d7304b3a83ee7f159cad0a9bdbe97019588ce836087b8fe3b0b2`,
which is the hash ADR 0002 pins for the layer builder, and it comes out pass
with 434,167 characters and 85 page breaks against pdfinfo's 85 pages.

What was tried and rejected: no threshold on layer length separates the
labelled bad set from the rest. The 24 bad layers run from 0 to 6,236
characters and 16 legitimate stored layers sit under 2,000, because a model
hub's `config.json` is a legitimate 900-character source. A length gate that
caught the negatives would cut real work, so the archive lane's capture-time
check keeps that job and this gate does not repeat it.

## Coverage, with the identity

`npm run layers -- coverage`

| Bucket | Sources | Characters |
| --- | --- | --- |
| `layer_pass` | 1,417 | 152,846,281 |
| `layer_suspect` | 13 | 1,870,059 |
| `layer_fail` | 0 | 0 |
| `no_normaliser` | 2 | 0 |
| `not_the_artifact` | 27 | 0 |
| `no_capture` | 24 | 0 |
| total | 1,483 | 154,716,340 |

1417 + 13 + 0 + 2 + 27 + 24 = 1483. Every source is in exactly one bucket,
and `tests/omics-layer-registry.test.ts` fails if that stops being true.

The character column counts a layer once per source that cites it, because
that is what an extractor reads. Counted once, the same text is 124,719,037
characters over 1,120 distinct layers. A source's figure is its best layer,
not the sum of the layers under its object: a supplement zip holding five
passing PDFs counts the longest one, and the other four stay in the registry
to be asked for by object.

`layer_fail` is zero because the eight failing layers all sit under objects
whose source is already in `not_the_artifact`, or are supplement members of a
source whose paper has a passing layer. The bucket is exercised by a fixture in
the test rather than by the store.

## The extraction surface

`npm run layers -- surface`

**1,430 of 1,483 sources have a usable layer.** That is 96.43% of sources, and
it is the ceiling on the recollection's coverage until one of the obstacles
below is removed. Of those, 1,417 are at pass and 13 at suspect, where suspect
means the layer is usable and carries a recorded caveat.

Two character figures, because they measure different things and the larger
one alone would overstate the corpus.

| Figure | Characters | What it counts |
| --- | --- | --- |
| Distinct | 124,719,037 over 1,120 layers | the text that exists |
| Per source | 154,716,340 | the reading, with a layer cited by two sources counted twice |

The distinct figure is the headline, because 1,120 layers serve 1,430
sources. 255 of those layers are the best layer for more than one source,
which accounts for the 310 extra source rows. By source class the shared
layers carry 265 europepmc-api sources, 214 code-repository, 35 other-web,
33 arxiv, 10 publisher, 4 pmc and 4 model-hub.

Characters per source: minimum 32, median 20,845, p95 172,627, maximum
20,823,442.

| Source class | Sources | Usable | Characters |
| --- | --- | --- | --- |
| code-repository | 601 | 593 | 16,278,725 |
| europepmc-api | 485 | 474 | 63,670,832 |
| arxiv | 83 | 83 | 7,717,642 |
| other-web | 91 | 75 | 41,686,091 |
| model-hub | 67 | 54 | 373,003 |
| preprint-server | 52 | 52 | 6,981,969 |
| publisher | 66 | 64 | 16,092,213 |
| pmc | 28 | 28 | 1,545,120 |
| data-repository | 10 | 7 | 370,745 |

The 53 sources that are not extractable, and the work each one needs:

| Sources | Work | Lane |
| --- | --- | --- |
| 27 | a second capture route for a host that served a page instead of the source | the archive lane |
| 24 | a rescue wave against the host that refused the fetch | the archive lane |
| 1 | optical character recognition, which no layer makes verifiable | neither, by ADR 0002 |
| 1 | a reader for a binary format nothing here reads | the extractor lane |

The 24 that were never captured break down by the archive lane's own reasons:
8 network_error, 6 http_error, 5 not_found, 3 too_large, 1 paywalled_not_held,
1 rate_limited.

## The interface

```ts
import {
  layersForSource,  // (sourceId, root?) => LayerRecord[], best verdict first
  layersForObject,  // (objectSha256, root?) => LayerRecord[]
  layerByHash,      // (layerSha256, root?) => LayerRecord | null
  layerText,        // (record, root?) => string, re-derived and hash verified
  sliceSpan,        // (text, start, end) => { exact, start, end, byte_start, byte_end }
  characterCount,   // (text) => number, code points
} from "shared/omics/layers/index";
```

`layerText` re-derives the layer from the stored bytes and refuses to return
text whose sha256 is not the one the registry names, so a tool version that
moved under a stored span is an error rather than a silent relocation. Reading
a PDF layer costs a pdftotext run, so a caller working over many spans in one
layer reads it once and slices it many times.

`sliceSpan` takes the code point offsets `shared/omics/locator.ts` declares,
because that is what `oa:TextPositionSelector` counts, and returns the UTF-8
byte offsets beside them, because that is what the resolvers slice. JavaScript
string indices are neither.

`layerText` reads the object cache, which is gitignored and local. 296 of the
2,301 registry rows sit on restricted objects, so on a machine without the
cache those layers are not readable at all and the other 2,005 need the
published release asset first.

## What this does not do

The archive manifest holds 1,167 rows and every one of them is
`exact-bytes`. `shared/archive/layers/store.ts` writes `text-layer` rows and
no command calls it, so the derivation has never been run into the store.

ADR 0002's "one hash, one home" test therefore passes in part and not in
whole. Measured against the manifest: 479 of the 2,301 registry rows have a
`layer_sha256` that is already a manifest key, all 479 of them identity
layers, where the object is plain UTF-8 text and already is its own text
layer. The other 1,822 rows, over 1,643 distinct hashes, name bytes the store
does not hold under that key: 1,168 are container members and the rest are
PDF, XML, HTML and office layers that need an object written for them.

Those bytes are not lost. Every one of them re-derives from a stored object,
which `npm run layers -- check` proves over all 1,167, so `layerText` returns
them today. What is missing is the second home: until the archive lane stores
the layer objects, a reader has to re-derive rather than fetch, which costs a
pdftotext run per PDF and makes a layer only as available as poppler.

No model was called anywhere in this work.
