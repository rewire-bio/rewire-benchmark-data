"""Write ledger.jsonl and scope-audit.jsonl for the genomic foundation model pass (2026-10-11).

Usage: python3 -I build-ledger.py
Reads extract/querylog-raw.jsonl (written by the search scripts) and the per-query decisions below.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
LANE = "genomics"
CUTOFF = "2026-10-11"
REVIEWER = "Claude (Opus 5.5) research agent lit-gfm-2 scope review; not a scientific validation"
CLAIM = ("Bounded discovery pass over genomic foundation model evaluations and reviews posted 2025-10-01 to 2026-10-11, "
         "not systematic exhaustion or all-model coverage. Benchmark-suite papers were left to the parallel lit-genomics pass.")

BUZ = ["gfm2-20261011-buzkova2026-source"]
DAT = ["gfm2-20261011-datta2026-source"]
YOU = ["gfm2-20261011-you2026-source", "gfm2-20261011-you2026-source-supplement"]

DECISIONS = {
    1: ("Title-only sweep for foundation or language model benchmarks in DNA and genomics. Two hits, both in scope; the Evo 2 viral-architecture preprint was screened and kept as a candidate.", [], []),
    2: ("Main discovery sweep. Screened the 200 returned records by title; kept independent multi-model evaluations and reviews, excluded single-model method papers and the benchmark suites covered by lit-genomics. Led to the You et al. extraction.", YOU, []),
    3: ("Named-model sweep for variant-effect and zero-shot evaluations. Surfaced the Evo 2 blind-spots preprint, the AlphaGenome cross-species and ancestry-stratified evaluations and the personal-genome studies; none retrievable or tabular enough to extract in this pass except as candidates.", [], ["Mathur and Sachidanandam 2026 (Evo 2 blind spots) could not be retrieved: bioRxiv returned HTTP 429 twice."]),
    4: ("Long-range and long-context sweep. No new extractable comparison beyond DNALONGBENCH, which is a suite for lit-genomics.", [], []),
    5: ("Probing, linear-probe and frozen-embedding sweep. Confirmed the arXiv probing work found in query 7 and the Nucleotide GPT probing paper (no full text in Europe PMC).", [], []),
    6: ("Review and survey sweep. Seven genomic-language-model reviews read for their benchmark tables and reference lists (see the review-mining entry); none printed new benchmark results, so none was added as a source.", [], []),
    7: ("arXiv sweep for genomic foundation model benchmarks and evaluations. Led to the Datta et al. frozen-representation extraction; also surfaced the mechanistic-invariance and dark-regulome evaluations as candidates.", DAT, []),
    8: ("arXiv sweep by model name. Same candidate set as query 7 plus the shuffling-artifact study of BEND.", [], []),
    9: ("arXiv title sweep for reviews and surveys of DNA or genomic language models: zero hits in the window.", [], []),
    10: ("Sequence-to-function sweep for AlphaGenome, Borzoi and Enformer evaluations. Surfaced the personal-genome and cross-species evaluations; values are in figures or supplementary spreadsheets not read in this pass.", [], ["Spiro et al. 2026 (SAGE-net) and Drusinsky et al. 2026 personal-genome evaluations not extracted; per-model values are in figures."]),
    11: ("Fine-mapped and complex-trait variant sweep. Surfaced the ancestry-stratified Borzoi and AlphaGenome evaluation and the GPN-Star paper.", [], []),
    12: ("Evo 2 specific sweep for ClinVar, splice and non-coding evaluations. Only developer or single-condition studies in the window.", [], []),
    13: ("Broad sequence-to-function benchmark sweep: 886 hits, mostly protein and unrelated. Screened the first 150 by title; nothing new in scope.", [], ["Only the first 150 of 886 records were screened."]),
    14: ("Plant genomic language model sweep. PlantCAD2, PlantGFM and BOTANIC are developer papers; the Nullsettes evaluation was found here and screened.", [], []),
    15: ("MPRA, STARR-seq and enhancer sweep against genomic language models: nothing new in scope in the window.", [], []),
    16: ("Variant-effect sweep against conventional predictors (CADD, GPN-MSA, AlphaMissense, phyloP). Hits were protein-side or clinical; nothing new in scope.", [], []),
    17: ("TraitGym and causal-variant sweep: five hits, none new in the window.", [], []),
    18: ("Resolution query for the TraitGym benchmark paper. It is a 2025-02 preprint, before the window, and its suite belongs to the lit-genomics pass.", [], ["TraitGym (Benegas et al., bioRxiv 2025.02.11.637758) is outside the window and is not in the store; flagged for the benchmark-suite pass."]),
    19: ("Resolution query for three arXiv titles found by the arXiv sweeps. Only the Nullsettes paper is indexed in Europe PMC.", [], []),
    20: ("AlphaGenome comparison sweep. Surfaced the splice-annotation and synthetic-variant splicing benchmarks and the fine-mapping utility study; all screened, values in figures or supplements not read.", [], []),
    21: ("Zero-shot against fine-tuned sweep with that exact phrasing: zero hits.", [], []),
    22: ("Microbial and viral sweep for genomic foundation models. Led to the Buzkova et al. extraction.", BUZ, []),
}

EXTRA = [
    {"id": "search-lit-gfm2-q23", "query": "arXiv 2026 independent evaluation genomic language models variant effect prediction zero-shot Evo 2 Nucleotide Transformer comparison",
     "channels": ["web_search"], "searched_at": "2026-10-11T00:40:40Z", "status": "screened",
     "included_record_ids": [], "reviewed_source_ids": [],
     "decision": "Web search for independent arXiv evaluations. Returned the EVEE probe paper and the GENERator preprint, both developer work; treated as leads only and not extracted.",
     "gaps": ["No independent arXiv benchmark of Evo 2 against the Nucleotide Transformer on zero-shot variant effects was found through web search."]},
    {"id": "search-lit-gfm2-review-mining", "query": "Reference and benchmark-table mining of seven genomic language model reviews: PMC12805252, PMC12558637, PMC12953581, PMC12947584, PMC12888390, PMC13174389, PMC13171353, PMC13489403",
     "channels": ["europe_pmc_fulltext"], "searched_at": "2026-10-11T00:41:30Z", "status": "screened",
     "included_record_ids": [], "reviewed_source_ids": [],
     "decision": "Read each review's tables and reference list for primary evaluations. The reviews print model inventories and task summaries, not new benchmark results, so none became a source. Their cited evaluations resolved to BEND, GUE, DART-Eval, GenBench, Genomics Long-Range Benchmark, Genomic Touchstone, BEACON, DNALONGBENCH, GUANinE and TraitGym (benchmark suites, left to lit-genomics), and to Tang et al. 2025, Feng et al. 2025 and You et al. 2026 (already in the store or extracted here).",
     "gaps": ["Genomic Touchstone (bioRxiv 2025.06.25.661622), the Genomics Long-Range Benchmark and the Diverse Genomic Embedding Benchmark are cited by the reviews but are not in the store; they are suites for the lit-genomics pass."]},
    {"id": "search-lit-gfm2-handover-screen", "query": "Abstract screen of four leads handed over by lit-genomics: DOI:\"10.64898/2026.05.12.724296\", DOI:\"10.1093/nargab/lqag025\", DOI:\"10.64898/2026.03.24.714098\" (Europe PMC) and id_list=2606.30140 (arXiv API)",
     "channels": ["europe_pmc_rest", "arxiv_api"], "searched_at": "2026-10-11T01:33:08Z", "status": "screened",
     "included_record_ids": [], "reviewed_source_ids": [],
     "decision": "Screened by abstract. BGCs-Bench and the arXiv pre-training assessment are in scope and kept as candidates; the Evo 2 plant study is a low-priority single-model candidate; the promoter tokenisation study is excluded as a method study. None extracted in this pass.",
     "gaps": ["BGCs-Bench (10.64898/2026.05.12.724296) and arXiv:2606.30140 were not retrieved; their tables are unchecked."]},
    {"id": "search-lit-gfm2-retrieval", "query": "Primary-artifact retrieval and hashing for the three extracted sources (biorxiv full PDF, arXiv PDF, Europe PMC XML and supplementaryFiles)",
     "channels": ["biorxiv_full_pdf", "arxiv_pdf", "europe_pmc_fulltext", "europe_pmc_supplementary"], "searched_at": "2026-10-11T00:55:34Z",
     "status": "included", "included_record_ids": BUZ + DAT + YOU, "reviewed_source_ids": BUZ + DAT + YOU,
     "decision": "Retrieved and hashed each artifact, then parsed its text layer. Bytes are archived only for the CC BY source (Buzkova et al.); the arXiv licence and the CC BY-NC-ND article are recorded by hash and locator alone.",
     "gaps": ["The Europe PMC supplementaryFiles zip is assembled per request, so only the member PDF hash is bound for You et al."]},
]

rows = []
for i, line in enumerate(open(HERE / "querylog-raw.jsonl"), 1):
    q = json.loads(line)
    decision, included, gaps = DECISIONS[i]
    rows.append({
        "id": f"search-lit-gfm2-q{i}", "lane": LANE, "query": q["query"],
        "channels": [q["channel"]], "searched_at": q["searched_at"], "cutoff_date": CUTOFF,
        "status": "included" if included else "screened",
        "included_record_ids": included, "reviewed_source_ids": included,
        "decision": f"{q['hits']} hits. {decision}", "gaps": gaps, "coverage_claim": CLAIM,
    })
for extra in EXTRA:
    rows.append({**extra, "lane": LANE, "cutoff_date": CUTOFF, "coverage_claim": CLAIM})

with open(OUT / "ledger.jsonl", "w") as f:
    for row in rows:
        f.write(json.dumps({k: row[k] for k in ["id", "lane", "query", "channels", "searched_at", "cutoff_date",
                                                "status", "included_record_ids", "reviewed_source_ids", "decision",
                                                "gaps", "coverage_claim"]}, ensure_ascii=False) + "\n")
print(len(rows), "ledger entries")
