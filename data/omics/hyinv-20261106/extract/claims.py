"""Descriptive claims for the HyInv batch: model identity, training, panels,
baseline settings, the application tasks and the report's own caveats.

Each claim quotes or paraphrases one pinned source location. Nothing here is a
measurement on a benchmark panel; those are results.
"""

from entities import (
    B, BENCHMARK, MODEL, SRC_LICENCE, SRC_README, SRC_REPO, SRC_REPORT, record,
)
from evidence import REVIEW

CLAIMS = [
    # Model identity, inputs, outputs, availability, licence.
    ("architecture", MODEL, [SRC_REPORT, SRC_README],
     "A message-passing graph network with 1,957,573 parameters following the encoder-decoder design "
     "of ProteinMPNN: width 128, 4 encoder layers and 3 decoder layers, each residue connected to its "
     "48 nearest neighbours with rotation- and translation-invariant distance and orientation "
     "features, random initialisation. The encoder runs once per backbone; the decoder predicts amino "
     "acid distributions at masked positions from the backbone and the observed sequence context. At "
     "inference the model needs neither a protein language model, a structure predictor nor an "
     "alignment.",
     "Section 2.1 'Architecture'; Appendix C 'Configuration'; AI4Science/hyinv/README.md opening "
     "paragraph"),
    ("inputs", MODEL, [SRC_REPORT, SRC_README],
     "Protein backbone N, CA, C and O coordinates read from the ATOM records of the first model of a "
     "PDB file (MSE treated as MET), optionally a chain selection and a set of fixed residues given "
     "by PDB residue number. Each residue takes one slot and residues with missing backbone atoms "
     "keep their slot and are designed; residues are numbered 0..n-1 within each chain without "
     "filling gaps in the PDB numbering. mmCIF must be converted to PDB first. For multi-chain "
     "structures fixed positions must be qualified with a chain name.",
     "AI4Science/hyinv/README.md 'Usage' and 'Notes'; Section 2.1"),
    ("outputs", MODEL, [SRC_README],
     "Designed amino-acid sequences over the 20 standard amino acids, written as FASTA by the command "
     "line or returned as a list of strings by the Python API; chains are separated by '/' in the "
     "output and fixed positions are kept unchanged.",
     "AI4Science/hyinv/README.md 'Usage' and 'Notes'"),
    ("licence", MODEL, [SRC_LICENCE, SRC_README],
     "MIT. The package LICENSE carries two copyright lines, 'Copyright (c) 2022 Justas Dauparas "
     "(ProteinMPNN)' and 'Copyright (c) 2026 HyInv contributors', because the model modules come from "
     "ProteinMPNN, which is also MIT. The repository's own top-level LICENSE is Apache-2.0, so the "
     "package licence and the repository licence differ.",
     "AI4Science/hyinv/LICENSE; AI4Science/hyinv/README.md 'Citation and license'; repository "
     "README.md 'License'"),
    ("availability", MODEL, [SRC_README, SRC_REPO],
     "Public. The hyinv package, its command line and Python API and the FP32 weights "
     "(weights/model.safetensors, 7.8 MB, with config.json) ship in AI4Science/hyinv/ of the "
     "Tencent-Hunyuan/Hyra-results repository; the repository README states the 7.8 MB weights ship "
     "in the folder. Python 3.10+ and PyTorch, with safetensors and numpy; accelerated inference also "
     "needs triton. Runs on CPU and GPU. No hash or revision is published for the weights file.",
     "AI4Science/hyinv/README.md 'Installation' and 'Layout'; repository README.md 'Model releases'"),
    ("release_date", MODEL, [SRC_REPO],
     "Announced in the repository README's news list on 2026-11-02 as one of two protein models "
     "released with weights and code, alongside HyPLM-Flash. The technical report is dated "
     "2026-10-14.",
     "Repository README.md news entry '2026-11-02: Two protein models released with weights and "
     "code'; technical report title page"),
    ("developer", MODEL, [SRC_REPORT, SRC_REPO],
     "Released by Tencent Hunyuan and trained by the team's Hyra 2.0 research agent. The named "
     "authors of the technical report are Haowei Lin, Cai Zhou and Xiangxin Zhou, all affiliated with "
     "Tencent Hunyuan.",
     "Technical report 'Author Information' and Abstract; repository README.md header and 'Model "
     "releases'"),
    ("sampler", MODEL, [SRC_REPORT, SRC_README],
     "Deployment samples in 16 decoder passes after one encoder pass: the positions are split at "
     "random into 8 fixed equal-size groups, 8 rounds of blind drafting at temperature 0.6 sample one "
     "group each from the all-masked state, then 8 rounds of rewriting at temperature 0.34 mask and "
     "resample one group at a time with all other positions visible. The group permutation is drawn "
     "from a SHA-256 hash of the seed and the chain identifier and is independent of structure, "
     "sequence and weights. Truncation at inference uses top-p 0.9 and min-p 0.1. Fixed residues are "
     "visible as the native residue from the first round and are redrawn unchanged at every stage.",
     "Sections 3.1 and 3.2; Appendix E 'Procedure and groups' and 'Random streams, truncation and "
     "fixed residues'; AI4Science/hyinv/README.md opening paragraph"),
    ("reproducibility", MODEL, [SRC_README],
     "Outputs are identical for the same seed, batch size (default 64, automatically tightened by "
     "length), device type and PyTorch version. Each batch has its own random stream (batch k uses "
     "seed+k), so changing the batch size changes the result, and the CPU and GPU random streams "
     "differ, so their sequences are not identical.",
     "AI4Science/hyinv/README.md 'Notes'"),
    ("training", MODEL, [SRC_REPORT],
     "Two stages. Supervised: 627,945 structures, random-order likelihood objective, 85,000 updates, "
     "windows up to 512, AdamW with beta (0.9, 0.98), a Noam learning-rate schedule and label "
     "smoothing 0.1. Reinforcement learning: 50,000 backbones, a reward with a leave-one-out "
     "advantage over 32 candidates per backbone, 640 updates of a 656-update run, batches of 256 "
     "backbones by 32 candidates, AdamW with beta (0.9, 0.95), a constant learning rate of 2e-5, a KL "
     "penalty of 0.005 then 0.001 to the fixed supervised checkpoint, and sampling at temperature "
     "0.3. The reward is scTM computed with ESMFold2 and TM-align; a ProteinMPNN-derived bounded "
     "likelihood contrast supplies five percent of it as a model-derived stability proxy, which the "
     "report states is not a stability measurement. Native sequence recovery has weight zero.",
     "Table 4 'Training configuration'; Appendix C 'Reward and stability proxy' and 'RL objective'"),
    ("training_data", MODEL, [SRC_REPORT],
     "The supervised corpus holds 627,945 unique sequences: records need a valid-residue ratio of at "
     "least 0.95 and canonical residues only, predicted structures a mean pLDDT of at least 85, and "
     "source weights give experimental structures about 70% and predicted structures about 30% of the "
     "expected loss mass. The reinforcement-learning pool holds 50,000 backbones (16,839 "
     "experimental, 33,161 predicted; mean length 254, range 48 to 512) under the same quality rules, "
     "with at most one predicted record per cascaded 50%-identity MMseqs2 cluster and at most two "
     "experimental records per cluster, drawn with weights that favour harder backbones.",
     "Appendix C 'Data and pool', first two bullets"),
    ("training_evaluation_overlap", MODEL, [SRC_REPORT],
     "The authors state: 'We do not claim zero sequence overlap between the training data and the "
     "evaluation panels.' The reinforcement-learning pool was filtered against the benchmark panels "
     "with a same-source homology mask built from MMseqs2 searches of the candidate records against "
     "the benchmark sequences, excluding a record if it is positive under the mask and using a record "
     "only if that search queried it; the supervised corpus was filtered by exact-sequence removal "
     "and a homology filter. For the application panels Appendix G's screen is a coverage rule: a hit "
     "counts only if its identity is at least 0.3 and it covers at least 0.8 of the query or of the "
     "target, so partial hits remain, and the report says a backbone passing the rule is "
     "homology-filtered at these thresholds, 'which is weaker than having no similar fragment in the "
     "library'.",
     "Appendix C 'Data and pool', third and fourth bullets; Appendix G 'Homology of the panels'; "
     "Table 10"),
    ("predicted_not_experimental", MODEL, [SRC_REPORT],
     "Every quantity the report measures is computed on predicted structures and designed sequences. "
     "Appendix B states that none is an experimental measurement, and Appendix G repeats this for the "
     "application tasks. No binding, expression, stability or catalytic activity was measured, so no "
     "biological efficacy follows from any of these scores.",
     "Appendix B opening sentence; Appendix G opening paragraph"),
    ("scope", MODEL, [SRC_REPORT],
     "HyInv targets single-chain backbones. The report names designing for multi-chain interfaces and "
     "membrane environments as a natural next step, so neither is claimed. ProteinZero V2, one of its "
     "two reference baselines, is declared by its own authors for backbones of up to 100 residues and "
     "is run here on the full panels.",
     "Section 7 'Conclusion'; Appendix D.1"),
    # Benchmark-level facts.
    ("panels", BENCHMARK, [SRC_REPORT],
     "Six panels. Five test panels: CATH4.3 test (1,882 chains, 103 clusters), CATH4.2 test (1,120, "
     "109), TS500 (500, 500), TS50 (50, 50) and RecentPDB (121, 121), all folded by ESMFold2, with "
     "RecentPDB also folded by Boltz2 and Protenix2. CATH4.3 validation (1,529 chains, 91 clusters) "
     "is the development panel: it fixed the sampler setting and the checkpoint and monitored "
     "training, and each test panel was evaluated once. CATH4.3 test and RecentPDB also served as the "
     "sampler check. The resampling unit is the CATH topology cluster on the two CATH panels and the "
     "single chain elsewhere.",
     "Table 3 'Evaluation panels'; Section 5.1 'Panels'; Appendix A 'Panels'"),
    ("checkpoint_selection", BENCHMARK, [SRC_REPORT],
     "The checkpoint and the sampler setting were chosen on the development panel alone. The "
     "checkpoint is the latest reinforcement-learning snapshot whose development scTM at diversity "
     "0.30 is within 0.002 of the best (update 640); the best-scoring snapshot differs from it by "
     "-0.0004, below the noise of one evaluation. The default sampler setting (draft 0.6, rewrite "
     "0.34, development diversity 0.30) was read off the development curve before the test panels "
     "were generated with this checkpoint. The development panel also chose the "
     "reinforcement-learning learning rate and training configuration.",
     "Appendix A 'Checkpoint and sampler setting'"),
    ("run_to_run_variation", BENCHMARK, [SRC_REPORT],
     "Two independent generate-and-fold runs of the same policy and sampler on the development panel "
     "differ by -0.0008 and +0.0016, so one evaluation carries noise of about +/-0.0015 scTM; "
     "refolding identical sequences with other fold seeds moves a panel mean by less than 0.0002. The "
     "report states that differences between checkpoints below about 0.003 are not resolvable.",
     "Appendix A 'Run-to-run variation'"),
    ("baseline_reproduction_check", BENCHMARK, [SRC_REPORT],
     "Some ESMFold2 cells were regenerated for the report with the same weights, temperature and "
     "sampler. A regenerated cell is used only where the same procedure reproduces the released score "
     "on RecentPDB; the printed absolute scTM differences are 0.0009 (ProteinMPNN grouped, CATH4.3 "
     "test), 0.0007 (ProteinMPNN low-noise grouped, four panels), 0.0006 (ProteinZero V2 ESM1, "
     "CATH4.3 test), 0.0004 (PiFold), 0.0022 (CMLM), 0.0005 (LM-Design 650M), 0.0001 (DPLM-2 3B) and "
     "0.0005 (LigandMPNN), each on four panels unless stated, all within 0.003. The fraction of "
     "identical sequences is 100.0% for every baseline except DPLM-2 3B at 99.2%. ProteinMPNN and "
     "ProteinZero V2 (ESM2) were not regenerated. All RecentPDB cells under the three predictors are "
     "released values, and the ProteinMPNN temperatures other than the published one were generated "
     "for this report.",
     "Table 5 'Baseline settings, weights and reproduction check' and the paragraph after it"),
    ("baseline_diversity_mismatch", BENCHMARK, [SRC_REPORT],
     "The ten baselines are single published settings at one temperature each, not tuned to the "
     "panels, so comparisons are at comparable rather than exactly equal diversity. Of the 70 "
     "comparisons (ten baselines in seven panel-predictor columns) all 70 point estimates favour "
     "HyInv and 61 have an interval that excludes zero; the nine that include zero are ProteinMPNN "
     "(TS500, TS50), ProteinMPNN grouped (TS50), ProteinZero V2 ESM1 (CATH4.3 test, TS500, TS50), "
     "ProteinZero V2 ESM2 (CATH4.3 test, TS50) and LigandMPNN (TS50). PiFold, CMLM, LM-Design and "
     "DPLM-2 3B are single points at much lower diversity than HyInv, so their differences are not at "
     "matched diversity. ProteinMPNN is the only baseline with a temperature sweep, and it is the "
     "only baseline for which the report reads an equal-diversity difference. HyInv's diversity is "
     "above ProteinMPNN with a clear interval on CATH4.3 test and CATH4.2 test and above ProteinZero "
     "V2 (ESM2) on the same two panels, but 0.015 below ProteinZero V2 (ESM2) on RecentPDB; at the "
     "development curve's slope of 0.07 scTM per unit of diversity the report puts the largest offset "
     "(0.016) at a worth of at most 0.0011 scTM.",
     "Appendix D.1, D.2 and D.3; Appendix A 'Scores at equal diversity'; Section 5.2"),
    ("predictor_independence", BENCHMARK, [SRC_REPORT],
     "ESMFold2 is the primary structure predictor and also the reinforcement-learning reward "
     "predictor, so RecentPDB is folded in addition by Boltz2 and Protenix2, which never enter "
     "training. Those two run with the alignment built from the designed sequence by MMseqs2 against "
     "UniRef50, and the report states that their scores partly reflect resemblance to a natural "
     "family and serve as a robustness check. The reward itself used an accelerated ESMFold2 that is "
     "not bit-identical to the evaluation model; a seed-matched test on 78 sequences gives a median "
     "absolute scTM difference of 9e-5, and all evaluation numbers use the original recipe.",
     "Section 5.3; Appendix A 'Folding and seeds'; Appendix C 'Optimization and parallel execution', "
     "fourth bullet"),
    # Inference and engineering facts that are not panel measurements.
    ("inference_speed_conditions", MODEL, [SRC_REPORT, SRC_README],
     "Latencies were measured on one NVIDIA H20 (Hopper class, sm_90) of a node on which nothing else "
     "ran, with PyTorch 2.7.1 and CUDA 12.9. The timed region excludes model loading, CUDA graph "
     "capture and kernel compilation; a first call costs 67.7 ms to 834 ms per shape bucket in the "
     "report's accounting, and the package README puts cold-cache Triton compilation at about 25 s "
     "for the exact path and 14 s for the BF16 path, plus about 0.1 to 0.2 s to capture a graph for a "
     "new shape. The kernels were verified on an H20 only and have not been verified on other "
     "architectures. HyInv's timing rows used the supervised-stage weights and a rewrite temperature "
     "of 0.23, not the released checkpoint's default. Baselines ran with their released "
     "implementations in FP32 without graph capture or compilation, DPLM-2 3B in BF16 autocast, and "
     "unbatched where the released adapter handles one structure per call, so the report states the "
     "speed-ups are against those implementations and not against the best achievable speed of the "
     "baseline models.",
     "Appendix F 'Timing protocol' and 'Baseline timings'; Table 1 footnote; "
     "AI4Science/hyinv/README.md 'Accelerated inference'"),
    ("library_scale", MODEL, [SRC_REPORT],
     "A library of 10,000 sequences for one 250-residue backbone takes 2.11 s on one GPU (4,740 "
     "sequences per second) against 129.1 s for the reference sampler and 142.0 s for ProteinMPNN, "
     "and 0.253 s on eight GPUs (39,527 sequences per second, 7.7 times the single-GPU rate at the "
     "same batch size); the single-GPU rate is 5,430 sequences per second at candidate batch 128. For "
     "128 candidates at 402 residues and a batch of 32 the peak memory allocated by tensors is 811 "
     "MiB for the BF16 path, 4,323 MiB for the reference sampler and 3,164 MiB for ProteinMPNN.",
     "Appendix F 'Library scale and memory'; Section 4"),
    ("numerical_paths", MODEL, [SRC_REPORT, SRC_README],
     "Two accelerated paths. The exact FP32 path computes matrix products by a three-pass TF32 "
     "emulation of FP32 with erf GELU and returns the reference sampler's sequences for the same "
     "seeds (1,600 of 1,600 eager, 400 of 400 with graph capture, 352 of 352 in padded multi-target "
     "batches), with graph replay equal to eager execution bit for bit; the report calls only this "
     "path identical. The BF16 path uses BF16 operands with FP32 accumulation and tanh GELU and is a "
     "numerically different path: against the reference on 200 development backbones the largest "
     "absolute logit difference is 0.069, the mean KL divergence per sampled position 5.2e-5 (99th "
     "percentile 7.5e-4), the argmax agrees at 99.73% of positions and, with the same seeds, 49.4% of "
     "sequences are identical and 98.7% of positions agree. All sequences scored in Section 5 come "
     "from the reference sampler.",
     "Appendix F 'The two numerical paths'; Section 4 'Quality'; AI4Science/hyinv/README.md "
     "'Accelerated inference'"),
    ("readme_speed_discrepancy", MODEL, [SRC_README, SRC_REPORT],
     "The package README's own speed figures differ from the report's for the exact FP32 path: about "
     "119 / 281 ms for 148 / 402 residues against the report's 130 / 303 ms. The README states the "
     "reason, that the report's exact path uses another set of kernels, and gives the BF16 and "
     "reference numbers as the report's (about 25 / 54 ms against 24.7 / 50.6 ms, and 999 / 2,633 "
     "ms). The report's values are the ones recorded as results here.",
     "AI4Science/hyinv/README.md 'Accelerated inference', speed paragraph; Table 1"),
    ("decoding_rounds_ablation", MODEL, [SRC_REPORT],
     "The default of 8 draft and 8 rewrite rounds was kept because shorter schedules cost more "
     "quality than they save time: the scTM at fixed diversity of six schedules with fewer rounds "
     "(6+8, 4+8, 8+6, 8+4, 6+6 and 4+4 draft and rewrite rounds) is lower than the 16-pass default by "
     "0.0028 to 0.0074. The per-schedule values appear only in Figure 8b, which prints no cell "
     "labels, so only the range is recorded.",
     "Appendix F 'Quality of the BF16 path', final sentences; Section 5.4 'Decoding rounds'; "
     "Figure 8b"),
    # Application tasks: single-case and display results, recorded as claims not results.
    ("application_pocket_library", BENCHMARK, [SRC_REPORT],
     "Pocket-constrained libraries. With the 15 ligand-contacting residues of a 148-residue binder "
     "fixed (backbone 9NZE, ligand A1B7L), 373 of 384 designs pass on that one backbone, which the "
     "report says is shown for display; the mean pass rate over twelve pocket backbones is 43%. A "
     "design passes if its scTM is at least 0.90 and its site CA RMSD at most 1.0 Angstrom. The five "
     "displayed designs have scTM 0.98 to 0.99, pocket RMSD 0.37 to 0.73 Angstrom and 41 to 50% "
     "pairwise identity. The panel is 12 backbones, ten chosen by rule and two single cases chosen "
     "earlier, with 384 designs per backbone and cell; the endpoint is the number of distinct "
     "sequences after clustering at 50% identity among the passing designs of a plate, against "
     "ProteinMPNN at the temperature whose diversity at the free positions is closest to HyInv's. "
     "Retention of the pinned residues is a check of the code and not a result.",
     "Section 6 'Pocket-constrained libraries'; Figure 10 panels a and c; Appendix G "
     "'Pocket-constrained libraries'"),
    ("application_enzymes", BENCHMARK, [SRC_REPORT],
     "Enzymes with the catalytic site kept. With the catalytic residues fixed, HyInv redesigns TEM-1 "
     "beta-lactamase (1BTL, 263 aa), subtilisin BPN' (2ST1, 275 aa) and IsPETase (5XJH, 300 aa) and "
     "keeps the predicted catalytic geometry at the level of the natural sequence; the displayed "
     "designs have catalytic heavy-atom RMSD 0.67, 0.71 and 0.23 Angstrom. The report states that the "
     "named enzymes are homologous to the training data and were chosen for display, and that the "
     "figure illustrates the preservation of a fixed geometry, not the design of new enzymes. Figure "
     "11c prints median catalytic-site RMSD bars for HyInv, ProteinMPNN and the native sequence over "
     "128 designs per method, but the bar order cannot be recovered from the text layer, so those "
     "nine values are recorded as a gap rather than read by eye.",
     "Section 6 'Enzymes with the catalytic site kept'; Figure 11 panels a and c; Appendix G 'Loop "
     "and window redesign and named enzymes'; Table 10 row 'Named enzymes'"),
    ("application_loops", BENCHMARK, [SRC_REPORT],
     "Loop redesign. HyInv redesigns loop windows of 16 to 25 residues in a fixed context, with the "
     "window within 0.5 to 1.8 Angstrom of the experimental structure; the three displayed cases are "
     "9T2I (178 aa, window of 25, scTM 0.97, window RMSD 1.3 to 1.8 Angstrom), 10UT (156 aa, window "
     "of 16, scTM 0.99, 0.5 to 0.7 Angstrom) and 9SNE (172 aa, window of 20, scTM 0.96, 0.6 to 0.7 "
     "Angstrom), each the four highest-scTM designs of 128. The panel is 8 backbones chosen by rule "
     "plus 4 named enzymes, 128 designs per backbone and region, 24,672 designs in all; a design "
     "succeeds if its whole-chain scTM is at least 0.9 and the region CA RMSD after fitting the "
     "unchanged context is at most 1.5 Angstrom, and the success rate is read only where the native "
     "refold meets the criterion on a majority of backbones. No success rate is printed as a cell.",
     "Section 6 'Loop redesign'; Figure 12; Appendix G 'Loop and window redesign and named enzymes'"),
    ("application_homology_screen", BENCHMARK, [SRC_REPORT],
     "Homology screen of the application panels (Table 10). De novo backbones: 74 backbones, 0 with a "
     "passing hit, 28 with partial hits only. Pocket library: 12, 0, 7. Loop and window, strict: 2, "
     "0, 2. Loop and window, relaxed: 6, 0, 4. Named enzymes: 4 backbones, all 4 with a passing hit "
     "and 0 partial. A hit passes if its sequence identity to the pretraining library or to the "
     "benchmark reference set is at least 0.3 and it covers at least 0.8 of the query or of the "
     "target; partial hits stay below the coverage limit. Strict backbones have no passing hit, "
     "relaxed backbones relax one criterion of the strict rule, fixed before any design, and the "
     "named enzymes are homologous to training data by design. The report states the table documents "
     "the panel rule only.",
     "Table 10 'Homology screen of the application panels' and its footnote; Appendix G 'Homology of "
     "the panels'"),
    ("application_statistics", BENCHMARK, [SRC_REPORT],
     "For the application tasks, monomers are folded with ESMFold2 with one fold seed shared by all "
     "generators for the same backbone and chunk, so generators are paired, and a subset of cells is "
     "also folded with Boltz2 and Protenix2. Comparators are ProteinMPNN and ProteinZero V2 only. The "
     "diversity-matched baseline temperature is chosen from sequences alone, before any fold is read, "
     "as the grid value whose mean pairwise Hamming distance over the designed positions is closest "
     "to HyInv's; where HyInv has lower diversity than the lowest baseline temperature the match is "
     "as close as the grid allows. Differences are paired by backbone, averaged over designs first, "
     "with 95% percentile intervals from 10,000 resamples, and the report notes that with four to "
     "twelve backbones the intervals are wide. Intervals are not adjusted for multiple comparisons.",
     "Appendix G 'Predictors, comparators and statistics'"),
    ("reproducibility_of_report", BENCHMARK, [SRC_REPORT],
     "The report states that every number, table and figure in it is generated by scripts from result "
     "files, and that sampling is random so a rerun with other seeds changes individual designs "
     "within the reported intervals. Neither the result files nor the scripts are published with it, "
     "and no panel chain list or split manifest is published, so none of its values can be "
     "recomputed from the released artifacts.",
     "Appendix H 'Release and reproducibility'"),
    ("release_location", BENCHMARK, [SRC_REPORT, SRC_REPO],
     "Appendix H says the weights and inference code will be released at "
     "github.com/Tencent-Hunyuan/hyra-results/tree/main, a branch reference. The pinned sources of "
     "this batch are at commit 0dcc533cc9f8f76c90ecbfe944df816b6672328a of that repository, where the "
     "weights and code are present under AI4Science/hyinv/.",
     "Appendix H 'Release'; repository README.md 'Model releases'"),
]


def claims():
    out = []
    for field, subject, sources, value, locator in CLAIMS:
        slug = field.replace("_", "-")
        subject_slug = "hyinv" if subject == MODEL else "benchmark"
        out.append(
            record(
                f"{B}-claim-{subject_slug}-{slug}",
                "claim",
                f"HyInv report: {field.replace('_', ' ')}",
                "Descriptive fact read from the pinned sources at the locator given. Not a "
                "measurement on a benchmark panel.",
                {
                    "field": field,
                    "value": value,
                    "source_locator": locator,
                    "review": dict(REVIEW),
                },
                links=[{"relation": "subject", "target_id": subject}],
                sources=sources,
            )
        )
    return out
