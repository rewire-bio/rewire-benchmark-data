#!/usr/bin/env python3
"""Build batch.jsonl for the BenchBench-Cloning batch (issue #235).

Reads extract/tables.json, written by extract/parse_tables.py from the pinned arXiv
PDF text layer, and emits one JSONL record per line, sorted by ID.

Usage: python3 build.py   (run from the batch folder)
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TABLES = os.path.join(HERE, "extract", "tables.json")
OUT = os.path.join(HERE, "batch.jsonl")

P = "benchbench-cloning-20261106-"

PDF_SHA = "6f5044b1bbbd81ad86b23cb536e2cae6428e0d9126f11546041355518febdc39"
ABS_SHA = "f9e233e9c65ab7470e5817defe75e749436122d677da9e540d51b5384100ee65"
BLOG_SHA = "eb67d3c73b14e40232bb5ea7633c64572c893c60b4f22a225320dcbac20354bf"
TEXT_LAYER_SHA = "c52ec41e171a81180ed0b9110e6ff26999740a73d7ecf2ab1fd600591357a616"

PDF_URL = "https://arxiv.org/pdf/2610.33355v1"
ABS_URL = "https://arxiv.org/abs/2610.33355"
BLOG_URL = "https://www.benchling.com/blog/how-good-is-ai-at-molecular-biology"
REPO_URL = "https://github.com/benchling/benchbench-cloning"

RETRIEVED_AT = "2026-11-06T11:51:23Z"
DATE = "2026-11-06"

S_PAPER = P + "source-arxiv-v1"
S_ABS = P + "source-arxiv-abs"
S_BLOG = P + "source-benchling-announcement"

AREAS = ["dna-genomes"]
CONTEXTS = ["research"]
FACETS = {"areas": AREAS, "contexts": CONTEXTS}
FACETS_M = {"areas": AREAS, "contexts": CONTEXTS, "method_types": ["foundation_model"]}

B_SUITE = P + "benchmark-suite"
B_PD = P + "benchmark-protocol-development"
B_CD = P + "benchmark-construct-design"

D_TASKS = P + "dataset-tasks"
DS_PD = P + "data-protocol-development-tasks"
DS_CD = P + "data-construct-design-tasks"
DS_CD_DET = P + "data-construct-design-deterministic-only"
DS_CD_JUDGED = P + "data-construct-design-rubric-judged"

EV_SIM = P + "evaluator-cloning-simulator"
EV_DET = P + "evaluator-construct-design-deterministic-grader"
EV_JUDGE = P + "evaluator-rubric-judge-gpt-6-astra"
EV_AGREE = P + "evaluator-agreement-judge-claude-mythos-5-1"

PR_PD = P + "protocol-protocol-development-pass-rate"
PR_CD = P + "protocol-construct-design-pass-rate"
PR_AGG = P + "protocol-aggregate-score"
PR_P5 = P + "protocol-protocol-development-pass-at-5"
PR_P10 = P + "protocol-protocol-development-pass-at-10"
PR_SOLVED1 = P + "protocol-protocol-development-tasks-solved-once"
PR_SOLVEDALL = P + "protocol-protocol-development-tasks-solved-every-attempt"
PR_TASK_DET = P + "protocol-construct-design-per-task-deterministic"
PR_TASK_JUDGED = P + "protocol-construct-design-per-task-rubric-judged"

# ---------------------------------------------------------------- shared text

NOT_REPRODUCED = (
    "Reported measurement transcribed from the pinned preprint. Not independently "
    "reproduced; the benchmark code and task data were not retrievable."
)

ACCESS_GAP = (
    "The construct-design tasks, graders and reference solutions are said in footnote 1 "
    f"(page 3) to be available at {REPO_URL}. That URL returned HTTP 404 from both the web "
    f"page and the GitHub API on {DATE} at {RETRIEVED_AT}, a repository search for "
    "'benchbench-cloning' returned no results, and the repository is absent from "
    "benchling's public repositories. No code or data artifact was retrieved."
)

LICENCE_NOTE = (
    "The preprint is licensed CC BY 4.0 (arXiv abstract page). That covers the article "
    "text, not the benchmark code or task data, whose licence is unverified because the "
    "linked repository could not be retrieved."
)

SIMULATOR_LIMIT = (
    "Scores come from a cloning simulator and retrospective graders, not from constructs "
    "built at the bench; the authors state the simulator cannot capture every source of "
    "variation in reagents, handling, growth or reaction outcomes (Section 6.2)."
)

BOOTSTRAP = (
    "95% confidence intervals from 20,000 bootstrap resamples of the tasks, retaining all "
    "attempts of each sampled task (Section 3.4)."
)


def review(method, note, method_note=None, sha=PDF_SHA, url=PDF_URL):
    # method_note already carries the parser description; do not repeat it in note.
    if method_note and note.endswith(method_note):
        note = note[: -len(method_note)].rstrip()
    out = {
        "method": method,
        "reviewer": ["claude"],
        "reviewer_note": (
            "Claude (Opus 5) extraction agent. Extraction only: no independent review is "
            "claimed, and a different agent reviews this batch."
        ),
        "date": DATE,
        "artifact_sha256": sha,
        "retrieval_url": url,
        "note": note,
    }
    if method_note:
        out["method_note"] = method_note
    return out


PARSE_REVIEW_NOTE = (
    "Extraction: parsed from the pdftotext -layout text layer of the pinned PDF by "
    "extract/parse_tables.py, which locates each table by its own caption line and "
    "searches only the lines between the previous caption and that caption, because "
    "Figures 2, 3, 6 and E1 print the same numbers as Tables 2, G2 and E1. Every row "
    "label is asserted. extract/check_tables.py reparses the same cells independently, "
    "by column position rather than by row regex, and compares."
)

PARSE_METHODS = ["deterministic-table-parse", "pdf-text-parse", "source-hash-verification"]


def record(rid, kind, name, description, attributes, links=None, facets=None,
           sources=None, status="source_checked"):
    return {
        "id": rid,
        "kind": kind,
        "name": name,
        "description": description,
        "status": status,
        "facets": FACETS if facets is None else facets,
        "source_ids": [S_PAPER] if sources is None else sources,
        "links": links or [],
        "attributes": attributes,
    }


def link(relation, target):
    return {"relation": relation, "target_id": target}


def with_caveats(scope_note, caveats, extraction):
    """Fold caveats and the extraction note into scope_note.

    The task and evaluator kinds declare neither `limitations` nor `review`
    (shared/omics/attribute-registry.ts), and the store's convention for these kinds is to
    carry caveats in scope_note (for example
    lit-agents-20261013-biomlbench-task-tdcommons-herg). Nothing is dropped; it moves.
    """
    parts = [scope_note]
    if caveats:
        parts.append("Caveats: " + " ".join(caveats))
    parts.append("Extraction: " + extraction)
    return " ".join(p.strip() for p in parts if p and p.strip())


def slug(text):
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]*", out), f"bad slug from {text!r}"
    return out


SYSTEM_SLUGS = {
    "GPT-6 Astra": "gpt-6-astra",
    "GPT-6.1 Sol": "gpt-6-1-sol",
    "Claude Opus 5.5": "claude-opus-5-5",
    "Gemini 4 Argon": "gemini-4-argon",
    "Claude Mythos 5.1": "claude-mythos-5-1",
    "Grok 4.7": "grok-4-7",
    "Kimi K3": "kimi-k3",
    "Gemini 3.8 Flash": "gemini-3-8-flash",
}

MODEL_TEXT = {
    "GPT-6 Astra": (
        "Large language model served as gpt-6-astra over the OpenAI API, which plans "
        "molecular cloning experiments when driven by an agent harness and which also "
        "grades written construction plans against a rubric."
    ),
    "GPT-6.1 Sol": (
        "Large language model served as gpt-6.1-sol over the OpenAI API, which plans "
        "molecular cloning experiments when driven by an agent harness."
    ),
    "Claude Opus 5.5": (
        "Large language model served as claude-opus-5-5 over the Anthropic API, which "
        "plans molecular cloning experiments when driven by an agent harness."
    ),
    "Gemini 4 Argon": (
        "Large language model served as gemini-4-argon over the Vertex AI global "
        "endpoint, which plans molecular cloning experiments when driven by an agent "
        "harness."
    ),
    "Claude Mythos 5.1": (
        "Large language model served as claude-mythos-5-1 over the Anthropic API, which "
        "plans molecular cloning experiments when driven by an agent harness and which "
        "also scores other systems' construction plans as a second judge."
    ),
    "Grok 4.7": (
        "Large language model served as grok-4.7 over the xAI API, which plans molecular "
        "cloning experiments when driven by an agent harness."
    ),
    "Kimi K3": (
        "Large language model served as moonshotai/Kimi-K3 on Baseten, which plans "
        "molecular cloning experiments when driven by an agent harness."
    ),
    "Gemini 3.8 Flash": (
        "Large language model served as gemini-3.8-flash over Vertex AI with an API key, "
        "which plans molecular cloning experiments when driven by an agent harness."
    ),
}

HARNESS_SLUGS = {
    "Codex CLI 0.156.1": ("codex-cli", "Codex CLI", "0.156.1"),
    "Claude Code 2.1.289": ("claude-code", "Claude Code", "2.1.289"),
    "Gemini CLI 0.63.0, in-sandbox proxy": ("gemini-cli", "Gemini CLI", "0.63.0"),
    "Gemini CLI 0.63.0": ("gemini-cli", "Gemini CLI", "0.63.0"),
    "Grok Build 1.0.46": ("grok-build", "Grok Build", "1.0.46"),
    "Pi 1.0.3": ("pi", "Pi", "1.0.3"),
}

HARNESS_TEXT = {
    "codex-cli": (
        "OpenAI's command-line coding agent, which drives a model in a shell workspace "
        "with file access and tool use so it can read task files, run analyses and write "
        "an answer file."
    ),
    "claude-code": (
        "Anthropic's command-line coding agent, which drives a model in a shell workspace "
        "with file access and tool use so it can read task files, run analyses and write "
        "an answer file."
    ),
    "gemini-cli": (
        "Google's command-line agent, which drives a Gemini model in a shell workspace "
        "with file access and tool use so it can read task files, run analyses and write "
        "an answer file."
    ),
    "grok-build": (
        "xAI's agent harness, which drives a Grok model in a shell workspace with file "
        "access and tool use so it can read task files, run analyses and write an answer "
        "file."
    ),
    "pi": (
        "Vendor-independent agent harness that drives a hosted model in a shell workspace "
        "with file access and tool use, for models without a harness of their own."
    ),
}


def main():
    with open(TABLES, encoding="utf-8") as handle:
        data = json.load(handle)
    t = data["tables"]
    records = []
    add = records.append

    # ------------------------------------------------------------- sources
    add(record(
        S_PAPER, "source",
        "BenchBench-Cloning: Evaluating Molecular Cloning Design and Protocol Development (arXiv:2610.33355v1)",
        "Preprint introducing BenchBench-Cloning, a 65-task molecular cloning benchmark, "
        "and reporting eight language-model agent systems scored on it at three reasoning "
        "settings each.",
        {
            "url": PDF_URL,
            "version": "arXiv v1, dated 23 October 2026",
            "retrieved_at": RETRIEVED_AT,
            "artifact_sha256": PDF_SHA,
            "publication_status": "preprint",
            "media_type": "application/pdf",
            "licence": "CC BY 4.0",
            "article_licence": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)",
            "code_url": REPO_URL,
            "archive_member": "artifacts/arxiv-2610.33355v1.layout.txt.gz",
            "archive_sha256": TEXT_LAYER_SHA,
            "archive_note": (
                "The gzipped pdftotext -layout text layer of the pinned PDF is kept in the "
                "batch folder because every stored value was parsed from it. The PDF itself "
                "is refetchable at the versioned URL and is not archived; two downloads on "
                f"{DATE} were byte-identical."
            ),
            "access_note": ACCESS_GAP,
            "venue": "arXiv (cs.AI)",
            "year": 2026,
            "source_locator": "Whole preprint, 19 pages; Tables 1, 2, A1, B1, C1, D1, D2, E1, E2, F1, F3, G1, G2",
            "missing_metadata": {
                "doi": {
                    "reason": "unavailable",
                    "note": "The arXiv abstract page serves no citation_doi for this preprint.",
                },
                "code_licence": {
                    "reason": "unavailable",
                    "note": ACCESS_GAP,
                },
            },
            "limitations": [
                "Preprint, not peer reviewed. The benchmark is published by Benchling with "
                "DNAForge, and the authors both built the benchmark and ran every system on it.",
                SIMULATOR_LIMIT,
                "Ten of the fifteen construct-design tasks are graded in part by GPT-6 Astra "
                "as a rubric judge, which is also one of the eight evaluated systems; the "
                "authors record occasional grading inconsistency as a limitation (Section 6.2).",
                "The simulator reports only the first blocking error, so the failure "
                "categories in Tables E1 and E2 do not establish whether later steps would "
                "have succeeded (Section 6.2).",
                "Single-turn: the authors state the format does not reflect the multi-turn way "
                "scientists work with a model (Section 6.2).",
                ACCESS_GAP,
            ],
            "review": review(
                ["source-hash-verification", "pdf-text-parse"],
                "Downloaded twice on 2026-11-06 with identical bytes. The pinned PDF "
                "hashes to the recorded SHA-256 and its text layer to the recorded archive "
                "hash.",
            ),
        },
    ))

    add(record(
        S_ABS, "source", "arXiv abstract page for 2610.33355",
        "The arXiv listing page for BenchBench-Cloning, which carries the preprint's "
        "title, submission date and licence.",
        {
            "url": ABS_URL,
            "version": f"Abstract page as served on {DATE}",
            "retrieved_at": RETRIEVED_AT,
            "artifact_sha256": ABS_SHA,
            "publication_status": "preprint",
            "media_type": "text/html",
            "licence": "CC BY 4.0",
            "article_licence": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)",
            "source_locator": "citation_title, citation_date and the licence link",
            "missing_metadata": {
                "doi": {
                    "reason": "unavailable",
                    "note": "The page serves no citation_doi meta tag for this preprint.",
                },
            },
            "limitations": [
                "Mutable listing page; the hash describes one retrieval, although two "
                f"retrievals on {DATE} were byte-identical.",
                "Used only for the title, the 23 October 2026 date and the CC BY 4.0 licence "
                "of the article text.",
            ],
            "review": review(
                ["source-hash-verification", "automated-source-review"],
                "Fetched twice on 2026-11-06 with identical bytes. citation_title and "
                "citation_date match the preprint, and the page links "
                "creativecommons.org/licenses/by/4.0/.",
                sha=ABS_SHA, url=ABS_URL,
            ),
        },
        links=[link("companion_of", S_PAPER)],
    ))

    add(record(
        S_BLOG, "source", "How good is AI at molecular biology? (Benchling announcement)",
        "Benchling's announcement of the BenchBench-Cloning release, which gives the "
        "headline aggregate scores and situates the benchmark in the wider BenchBench suite.",
        {
            "url": BLOG_URL,
            "version": "Blog post dated 30 October 2026, as served on 2026-11-06",
            "retrieved_at": RETRIEVED_AT,
            "artifact_sha256": BLOG_SHA,
            "publication_status": "official_project_source",
            "media_type": "text/html",
            "source_locator": "Whole post, by Ashu Singhal, posted 30 October 2026",
            "missing_metadata": {
                "licence": {
                    "reason": "unreported",
                    "note": "Benchling web page, all rights reserved; hashed, not stored.",
                },
            },
            "limitations": [
                "Mutable company web page; the hash describes one retrieval.",
                "Announcement, not a primary record of the evaluation: it prints no "
                "denominators, confidence intervals or per-task results.",
                "The post gives no link to the benchmark repository.",
            ],
            "evidence_concerns": [
                {
                    "source_id": S_BLOG,
                    "message": (
                        "The post says Kimi K3's 8.8% highlights \"the gap between frontier "
                        "and open-weight models at this task\". The preprint's own Table 2 "
                        "puts Gemini 3.8 Flash, a hosted frontier model, at 8.6%, below Kimi "
                        "K3. The characterisation is not supported by the paper's ranking, so "
                        "claims resting on the post's framing are withheld from comparison."
                    ),
                    "source_locator": "Benchling announcement, paragraph beginning 'GPT-6 Astra led with a score of 30.6%'",
                    "artifact_sha256": BLOG_SHA,
                    "review_date": DATE,
                    "applies_to": [P + "claim-announcement-open-weight-gap"],
                },
            ],
            "review": review(
                ["source-hash-verification", "automated-source-review"],
                "Fetched on 2026-11-06 and hashed. Its 30.6%, 22.2%, 20.5%, 8.8%, 72% and "
                "27% figures were checked against Tables 2 and G1 of the preprint and "
                "agree; its open-weight framing does not, and is recorded as an evidence "
                "concern.",
                sha=BLOG_SHA, url=BLOG_URL,
            ),
        },
        links=[link("companion_of", S_PAPER)],
    ))

    # ---------------------------------------------------------- benchmarks
    add(record(
        B_SUITE, "benchmark", "BenchBench-Cloning",
        "Benchmark of 65 molecular cloning tasks that scores whether a language-model "
        "agent can work out which constructs a scientific objective needs and plan an "
        "executable construction route to them from supplied starting materials.",
        {
            "entity_level": "suite",
            "version": "As published in arXiv:2610.33355v1 (23 October 2026)",
            "task": "End-to-end molecular cloning experiment planning: construct design and protocol development",
            "executable_suite": False,
            "scope_note": (
                "65 tasks in two sets: 50 protocol-development tasks graded by execution in a "
                "cloning simulator, and 15 construct-design tasks graded by task-specific "
                "deterministic checks, of which ten also carry a rubric-based model judge. "
                + SIMULATOR_LIMIT
            ),
            "protocol_version": "arXiv:2610.33355v1",
            "source_locator": "Abstract; Section 3; Table 1; Appendix A",
            "missing_metadata": {
                "split": {
                    "reason": "inapplicable",
                    "note": "An evaluation-only suite with no training split; every task is scored.",
                },
                "run_documentation": {
                    "reason": "unavailable",
                    "note": ACCESS_GAP,
                },
            },
            "limitations": [
                ACCESS_GAP,
                LICENCE_NOTE,
                SIMULATOR_LIMIT,
                "Single-turn by design; the authors note scientists usually work with a model "
                "over several turns (Section 6.2).",
                "Target sequences for the protocol-development tasks are hidden, and the "
                "preprint names none of the 50 tasks individually.",
            ],
            "review": review(
                ["pdf-text-parse", "automated-source-review"],
                "Task counts 65, 50 and 15 read from the abstract and Section 3 and "
                "cross-checked against the Table 1 total (50) and the 15 rows of Tables A1 "
                "and G2.",
            ),
        },
        sources=[S_PAPER, S_ABS, S_BLOG],
    ))

    add(record(
        B_PD, "benchmark", "BenchBench-Cloning protocol-development set",
        "The 50 BenchBench-Cloning tasks in which an agent is given a desired construct "
        "and an inventory of starting materials and must submit a cloning protocol that a "
        "simulator executes to one isolated product.",
        {
            "entity_level": "challenge",
            "version": "As published in arXiv:2610.33355v1",
            "task": "Protocol development for a specified plasmid construct",
            "executable_suite": False,
            "scope_note": (
                "Products are circular plasmids of 2.8 kb to 15.2 kb, median 5.4 kb, derived "
                "from laboratory notebooks created by Benchling contributors. Each task supplies "
                "up to eight starting plasmids as GenBank or FASTA files with annotations and "
                "notes of material properties, plus documentation for a cloning protocol "
                "language of 42 operations and tools including Python, Biopython and Primer3-py. "
                "A protocol passes if it executes and ends with one isolated product matching "
                "the hidden target; alternative routes are accepted. Binary score per attempt."
            ),
            "source_locator": "Section 3.1; Table 1",
            "missing_metadata": {
                "split_manifest": {
                    "reason": "unavailable",
                    "note": "No per-task identifiers are printed, and " + ACCESS_GAP,
                },
            },
            "limitations": [
                "The preprint names none of the 50 tasks; they are described only by the nine "
                "dominant-constraint families of Table 1.",
                "Footnote 1 offers only the construct-design tasks, graders and reference "
                "solutions for download; it makes no release claim for this set. " + ACCESS_GAP,
                SIMULATOR_LIMIT,
            ],
            "review": review(
                PARSE_METHODS,
                "The 50-task total was checked against the Table 1 total row and against the "
                "sum of the nine family counts, both 50.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("part_of", B_SUITE), link("uses_data", DS_PD)],
    ))

    add(record(
        B_CD, "benchmark", "BenchBench-Cloning construct-design set",
        "The 15 BenchBench-Cloning tasks in which an agent is given a scientific objective "
        "with sequence records and supporting materials and must return the constructs the "
        "objective calls for, their annotated sequences and a construction plan.",
        {
            "entity_level": "challenge",
            "version": "As published in arXiv:2610.33355v1",
            "task": "Construct design from a scientific objective",
            "executable_suite": False,
            "scope_note": (
                "15 tasks derived from published studies, Addgene records or authored "
                "sequences. Six supply experimental records from the source study, such as "
                "sequencing reads or gel images. Agents return an annotated construct "
                "sequence, orderable primers where required, a construction plan and a written "
                "justification. Every task has a deterministic grader over the returned "
                "sequences, their source and the construction route; ten also use a "
                "rubric-based GPT-6 Astra judge of the written reasoning and plan, and for "
                "those the final score is the product of the deterministic result and the "
                "rubric score. An attempt passes at a final score of at least 0.9."
            ),
            "source_locator": "Section 3.2; Appendix A, Table A1",
            "limitations": [
                "Ten of the fifteen tasks are graded in part by GPT-6 Astra, which is also one "
                "of the eight evaluated systems; the paper reports no bias analysis for that "
                "arrangement, only agreement with a second judge (Appendix C).",
                "Table F1 records that the shipped grader result was revised for 48 of the 600 "
                "top-effort trials on review, so the reported scores embed a manual "
                "adjudication pass.",
                ACCESS_GAP,
            ],
            "review": review(
                PARSE_METHODS,
                "The 15-task total, the split of 10 rubric-judged and 5 deterministic-only "
                "tasks, and the 6 tasks supplying experimental records were all asserted "
                "while parsing Table A1, and the task names were asserted to match Table G2.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("part_of", B_SUITE), link("uses_data", DS_CD)],
    ))

    # ------------------------------------------------------------- dataset
    add(record(
        D_TASKS, "dataset", "BenchBench-Cloning task corpus",
        "The 65 BenchBench-Cloning task definitions with their scientist requests, "
        "starting-material inventories, sequence records, supporting experimental records, "
        "hidden target sequences and graders.",
        {
            "version": "As described in arXiv:2610.33355v1",
            "split": "Evaluation only; all 65 tasks are scored and none is held out for training",
            "total": 65,
            "species": "Not stated as a corpus property; tasks cover bacterial, plant, insulin, "
                       "human cell line and synthetic-chromosome material",
            "assay": "In silico cloning simulation and retrospective grading; no wet-lab assay",
            "access": (
                "Not openly downloadable as checked. Footnote 1 (page 3) offers the "
                f"construct-design tasks, graders and reference solutions at {REPO_URL}; that "
                f"URL returned HTTP 404 on {DATE}. The protocol-development tasks, their hidden "
                "target sequences and the cloning simulator are not offered for download "
                "anywhere in the preprint."
            ),
            "repository": REPO_URL,
            "reuse_restrictions": LICENCE_NOTE,
            "source_locator": "Sections 3.1 and 3.2; footnote 1 (page 3); Table A1",
            "missing_metadata": {
                "accession": {
                    "reason": "unavailable",
                    "note": "No accession, archive DOI or data citation is given.",
                },
                "manifest": {
                    "reason": "unavailable",
                    "note": ACCESS_GAP,
                },
                "label_semantics": {
                    "reason": "unavailable",
                    "note": "Hidden target sequences and grader rubrics were not retrievable; "
                            + ACCESS_GAP,
                },
            },
            "scope_note": (
                "65 task definitions, evaluation only. Caveats: " + ACCESS_GAP + " " + LICENCE_NOTE
                + " The 50 protocol-development tasks come from laboratory notebooks created by "
                "Benchling contributors, which are not public, and the preprint gives no "
                "per-notebook provenance. Six construct-design tasks reuse experimental records "
                "from published studies; the preprint cites the studies but supplies no "
                "file-level provenance."
            ),
            "review": review(
                ["pdf-text-parse", "automated-source-review"],
                "Access rechecked on 2026-11-06 at 11:51:23Z: the GitHub web page and API "
                "both returned 404 and a repository search returned nothing. Nothing was "
                "downloaded, so no data artifact is hashed.",
            ),
        },
        sources=[S_PAPER],
    ))

    # ------------------------------------------------------ dataset subsets
    add(record(
        DS_PD, "dataset_subset", "BenchBench-Cloning protocol-development tasks (50)",
        "The 50 protocol-development task definitions: a scientist's request naming the "
        "desired construct, an inventory of up to eight starting plasmids with annotations "
        "and material-property notes, and a hidden target sequence.",
        {
            "version": "As described in arXiv:2610.33355v1 Section 3.1",
            "split": "Evaluation only",
            "eligible_count": 50,
            "subset_scope": "All 50 protocol-development tasks of the suite",
            "source_dataset": D_TASKS,
            "source_locator": "Section 3.1; Table 1 total row",
            "missing_metadata": {
                "exact_manifest": {
                    "reason": "unavailable",
                    "note": "No task identifiers are printed; " + ACCESS_GAP,
                },
            },
            "limitations": [
                "Individual tasks are not named in the preprint; only the nine "
                "dominant-constraint families of Table 1 are given.",
                ACCESS_GAP,
            ],
            "review": review(
                PARSE_METHODS,
                "Count 50 asserted against the Table 1 total row and the sum of the nine "
                "family counts.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("used_in", B_PD)],
    ))

    add(record(
        DS_CD, "dataset_subset", "BenchBench-Cloning construct-design tasks (15)",
        "The 15 construct-design task definitions: a scientific objective with sequence "
        "records and supporting materials, a deterministic grader, and for six of them "
        "experimental records taken from the source study.",
        {
            "version": "As described in arXiv:2610.33355v1 Section 3.2 and Table A1",
            "split": "Evaluation only",
            "eligible_count": 15,
            "subset_scope": "All 15 construct-design tasks of the suite",
            "source_dataset": D_TASKS,
            "source_locator": "Section 3.2; Table A1",
            "limitations": [
                "Six tasks reuse experimental records from the cited studies; the preprint "
                "gives no file-level provenance for them.",
                ACCESS_GAP,
            ],
            "review": review(
                PARSE_METHODS,
                "Count 15 asserted against the 15 rows of Table A1 and the 15 rows of Table "
                "G2, whose task names were asserted equal.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("used_in", B_CD)],
    ))

    a1 = {row["task"]: row for row in t["table_a1"]}
    judged_tasks = [r["task"] for r in t["table_a1"] if "rubric" in r["grading"]]
    det_tasks = [r["task"] for r in t["table_a1"] if "rubric" not in r["grading"]]
    assert len(judged_tasks) == 10 and len(det_tasks) == 5

    add(record(
        DS_CD_DET, "dataset_subset",
        "BenchBench-Cloning construct-design tasks graded deterministically only (5)",
        "The five construct-design tasks whose grading route is a task-specific "
        "deterministic check of the returned sequences, their source and the construction "
        "route, with no model judge.",
        {
            "version": "As described in arXiv:2610.33355v1 Table A1",
            "split": "Evaluation only",
            "eligible_count": 5,
            "subset_scope": "Tasks whose Table A1 grading column reads 'Deterministic': "
                            + "; ".join(det_tasks),
            "source_dataset": D_TASKS,
            "source_locator": "Table A1, column 'Grading', rows 1, 2, 3, 5 and 6",
            "review": review(
                PARSE_METHODS,
                "The five task names and their 'Deterministic' grading strings were asserted "
                "row by row while parsing Table A1.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("used_in", B_CD), link("same_data_as", DS_CD)],
    ))

    add(record(
        DS_CD_JUDGED, "dataset_subset",
        "BenchBench-Cloning construct-design tasks with a rubric model judge (10)",
        "The ten construct-design tasks whose final score is the product of a "
        "deterministic grader's result and a rubric-based model judge's score of the "
        "written reasoning and construction plan.",
        {
            "version": "As described in arXiv:2610.33355v1 Table A1",
            "split": "Evaluation only",
            "eligible_count": 10,
            "subset_scope": "Tasks whose Table A1 grading column reads 'Deterministic + "
                            "rubric judge': " + "; ".join(judged_tasks),
            "source_dataset": D_TASKS,
            "source_locator": "Table A1, column 'Grading', rows 4 and 7 to 15",
            "limitations": [
                "GPT-6 Astra is the judge and is also one of the eight evaluated systems "
                "(Section 3.3).",
                "Table F3 records that 34 of the 142 top-effort attempts that cleared the "
                "deterministic checks on these tasks were then scored below 0.9 by the judge.",
            ],
            "review": review(
                PARSE_METHODS,
                "The ten task names and their 'Deterministic + rubric judge' grading strings "
                "were asserted row by row while parsing Table A1.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("used_in", B_CD), link("same_data_as", DS_CD)],
    ))

    for family in t["table_1"]:
        add(record(
            P + "data-family-" + family["slug"], "dataset_subset",
            f"BenchBench-Cloning protocol-development tasks: {family['label'].rstrip()} "
            f"({family['tasks']})",
            "Protocol-development tasks whose dominant constraint, as classified by the "
            f"benchmark's authors, is {family['label'].rstrip().lower()}.",
            {
                "version": "As described in arXiv:2610.33355v1 Table 1",
                "split": "Evaluation only",
                "eligible_count": family["tasks"],
                "subset_scope": (
                    f"{family['tasks']} of the 50 protocol-development tasks "
                    f"({family['share_percent']}% of the set), grouped by the dominant "
                    "constraint the task imposes"
                ),
                "source_dataset": D_TASKS,
                "source_locator": f"Table 1, row '{family['label'].rstrip()}', columns 'Tasks' and 'Share'",
                "missing_metadata": {
                    "exact_manifest": {
                        "reason": "unavailable",
                        "note": "The tasks in each family are not named; " + ACCESS_GAP,
                    },
                },
                "limitations": [
                    "The families are the authors' own classification by dominant constraint, "
                    "and no task is named, so the grouping cannot be checked.",
                    "No result is reported per family: Table 1 gives only counts and shares.",
                ],
                "review": review(
                    PARSE_METHODS,
                    f"Count {family['tasks']} and share {family['share_percent']}% parsed from "
                    "the Table 1 row; the nine counts were asserted to sum to 50 and the nine "
                    "shares to 100.",
                    method_note=PARSE_REVIEW_NOTE,
                ),
            },
            links=[link("used_in", B_PD), link("same_data_as", DS_PD)],
        ))

    # ----------------------------------------------------------- evaluators
    add(record(
        EV_SIM, "evaluator", "BenchBench-Cloning cloning simulator",
        "Simulator that executes a submitted cloning protocol written in the benchmark's "
        "42-operation protocol language and returns a binary pass only when execution "
        "succeeds and ends with one isolated product matching the hidden target sequence.",
        {
            "version": "As described in arXiv:2610.33355v1 Sections 2 and 3.1",
            "task": "Simulated execution and binary grading of a cloning protocol",
            "scope_note": with_caveats(
                "Checks method-specific primer constraints, molecular-state and end-chemistry "
                "conditions, and the ability to produce and isolate multiple products. Invalid "
                "operations, incorrect sequences and unresolved mixtures fail. Alternative "
                "construction routes pass when they produce the same final product as the "
                "reference protocol. Each failed attempt is classified by the first error that "
                "blocks execution.",
                [
                    "The simulator reports only the first blocking error, so its failure "
                    "diagnostics do not establish whether later steps would have succeeded "
                    "(Section 6.2).",
                    SIMULATOR_LIMIT,
                    "The simulator is not offered for download anywhere in the preprint, and "
                    + ACCESS_GAP,
                ],
                "described from Sections 2, 3.1 and 6.2 of the pinned preprint. No simulator "
                "artifact was retrievable, so nothing is hashed and nothing was run.",
            ),
            "missing_metadata": {
                "profile": {
                    "reason": "unavailable",
                    "note": "The simulator is not offered for download anywhere in the "
                            "preprint, and " + ACCESS_GAP,
                },
            },
        },
        facets=FACETS, status="discovered",
        links=[link("part_of", B_PD)],
    ))

    add(record(
        EV_DET, "evaluator", "BenchBench-Cloning construct-design deterministic graders",
        "Task-specific deterministic graders that check a submitted construct's returned "
        "sequences, the sources those sequences come from and the construction route that "
        "is meant to build them.",
        {
            "version": "As described in arXiv:2610.33355v1 Sections 3.2 and 5.3",
            "task": "Deterministic grading of construct designs and construction routes",
            "scope_note": with_caveats(
                "One grader per task. Recorded failure modes include source references that "
                "cannot be resolved, one identifier used for different sequences, missing "
                "oligonucleotide tables, and fragments that no listed reaction produces. On "
                "the ten rubric-judged tasks the deterministic result is multiplied by the "
                "judge's rubric score.",
                [
                    "Table F1 records that the shipped grader result was revised for 48 of 600 "
                    "top-effort trials and 171 of 1800 across all lanes, on manual review of "
                    "the grader's evidence or after value-preserving re-expression of the "
                    "submitted record, so the reported pass rates embed a manual adjudication "
                    "pass.",
                    ACCESS_GAP,
                ],
                "described from Sections 3.2 and 5.3 and Appendix F of the pinned preprint; "
                "Tables F1 and F3 parsed by extract/parse_tables.py. No grader artifact was "
                "retrievable.",
            ),
            "missing_metadata": {
                "profile": {
                    "reason": "unavailable",
                    "note": ACCESS_GAP,
                },
            },
        },
        facets=FACETS, status="discovered",
        links=[link("part_of", B_CD)],
    ))

    add(record(
        EV_JUDGE, "evaluator", "BenchBench-Cloning rubric judge (GPT-6 Astra)",
        "Rubric-based model judge that scores an agent's written reasoning and "
        "construction plan on ten construct-design tasks, run on GPT-6 Astra, whose score "
        "multiplies the deterministic grader's result.",
        {
            "version": "GPT-6 Astra as the judge, arXiv:2610.33355v1 Section 3.3",
            "task": "Rubric-based scoring of written construct-design reasoning and plans",
            "scope_note": with_caveats(
                "Applies to the ten construct-design tasks whose Table A1 grading route is "
                "'Deterministic + rubric judge'. The final score is the product of the "
                "deterministic result and the rubric score, and an attempt passes at 0.9. "
                "The judge's most frequent recorded concern is that the plan does not lay out "
                "an orderable path from the supplied sources to the final product.",
                [
                    "The judge model is GPT-6 Astra, which is also one of the eight evaluated "
                    "systems; no analysis of self-preference is reported.",
                    "Model grading is stochastic and the authors record occasional grading "
                    "inconsistency (Section 6.2).",
                    "Agreement with a second judge does not establish independent scientific "
                    "validity, as the authors state (Section 6.2).",
                    "Table F3 records that 34 of the 142 top-effort attempts that cleared the "
                    "deterministic checks were then scored below 0.9 by the judge, so the "
                    "judge changes the reported outcome.",
                    "The rubric text, prompt and judge settings are not printed, and "
                    + ACCESS_GAP,
                ],
                "described from Sections 3.3 and 5.3 and Appendices A and F of the pinned "
                "preprint; Table F3 parsed by extract/parse_tables.py.",
            ),
            "missing_metadata": {
                "profile": {
                    "reason": "unreported",
                    "note": "The rubric text, prompt and judge settings are not printed, and "
                            + ACCESS_GAP,
                },
            },
        },
        facets=FACETS, status="discovered",
        links=[link("part_of", B_CD), link("uses_data", DS_CD_JUDGED)],
    ))

    add(record(
        EV_AGREE, "evaluator", "BenchBench-Cloning agreement judge (Claude Mythos 5.1)",
        "Second rubric judge, run on Claude Mythos 5.1, that regraded construct-design "
        "attempts blind to the reported outcome so that agreement with the shipped grades "
        "could be measured.",
        {
            "version": "Claude Mythos 5.1 as the second judge, arXiv:2610.33355v1 Appendix C",
            "task": "Independent regrading of construct-design attempts for agreement measurement",
            "scope_note": with_caveats(
                "Regraded every construct-design attempt of the first six systems evaluated "
                "(450 attempts: 6 systems, 15 tasks, 5 attempts). It saw the public task text, "
                "the private reference material and the submission files, but not the reported "
                "outcome, and returned a score on the same 0 to 1 scale; agreement is measured "
                "on the binary pass outcome at 0.9. It declined to grade 63 attempts under its "
                "own safety policy and those are excluded, leaving 387 graded trials.",
                [
                    "Covers only the first six systems evaluated, not Gemini 4 Argon or Claude "
                    "Mythos 5.1 itself.",
                    "63 of 450 attempts were declined under the judge's safety policy and "
                    "dropped, so the agreement figures rest on a self-selected subset.",
                    "The authors state that agreement between graders does not establish "
                    "independent scientific validity (Section 6.2).",
                ],
                "Appendix C text read and Table C1 parsed by extract/parse_tables.py; 450 minus "
                "63 declined equals the 387 'All trials' total, and both the two task slices "
                "and the six per-system slices were asserted to sum to 387.",
            ),
        },
        facets=FACETS, status="discovered",
        links=[link("part_of", B_CD)],
    ))

    # ---------------------------------------------------------------- tasks
    task_ids = {}
    for row in t["table_a1"]:
        name = row["task"]
        tid = P + "task-" + slug(name)
        task_ids[name] = tid
        judged = "rubric" in row["grading"]
        add(record(
            tid, "task", f"BenchBench-Cloning construct design: {name}",
            f"Construct-design task {row['number']} of BenchBench-Cloning, in which an "
            f"agent must design the constructs a scientific objective calls for, built on "
            f"{row['source_first_line']}.",
            {
                "version": "As published in arXiv:2610.33355v1 Table A1",
                "task_type": "construct design from a scientific objective",
                "metric": "count",
                "metric_direction": "higher",
                "metric_qualifier": "attempts passed out of 5, at a final score of at least 0.9",
                "scope_note": with_caveats(
                    f"Source: {row['source_first_line']}. Experimental records supplied: "
                    f"{row['records_first_line']}. Grading route: {row['grading']}."
                    + (
                        " The final score is the product of the deterministic grader's result "
                        "and a GPT-6 Astra rubric score of the written reasoning and plan, so "
                        "the outcome depends on the judge."
                        if judged else
                        " Deterministic checks only; no model judge."
                    ),
                    (
                        [
                            "Graded in part by GPT-6 Astra as a rubric judge, which is also "
                            "one of the eight evaluated systems.",
                        ] if judged else []
                    ) + [
                        "The preprint prints the task's source study and grading route but not "
                        "its request text or reference solution.",
                        ACCESS_GAP,
                    ],
                    f"row {row['number']} of Table A1 parsed by extract/parse_tables.py with "
                    "the task name and grading string asserted, and the name asserted to "
                    "appear in Table G2.",
                ),
                "splits": "Evaluation only; 5 attempts per system at each reasoning setting",
                "source_locator": f"Table A1, row {row['number']} '{name}'; Table G2, row '{name}'",
                "missing_metadata": {
                    "protocol": {
                        "reason": "unavailable",
                        "note": "The task text, grader and reference solution were not "
                                "retrievable; " + ACCESS_GAP,
                    },
                },
            },
            links=[
                link("part_of", B_CD),
                link("uses_data", DS_CD_JUDGED if judged else DS_CD_DET),
            ],
        ))

    # --------------------------------------------------------------- models
    model_ids = {}
    b1 = {row["system"]: row for row in t["table_b1"]}
    for system, system_slug in SYSTEM_SLUGS.items():
        row = b1[system]
        mid = P + "model-" + system_slug
        model_ids[system] = mid
        add(record(
            mid, "model", system, MODEL_TEXT[system],
            {
                "entity_level": "service",
                "reported_name": system,
                "version": f"Served as model id {row['model_id']} in October 2026",
                "access": (
                    f"Hosted model, reached over {row['access_route']}. No weights, "
                    "checkpoint hash or snapshot date is given."
                ),
                "source_locator": f"Section 3.3; Table B1, row '{system}'",
                "missing_metadata": {
                    "licence": {
                        "reason": "unreported",
                        "note": "The preprint gives no model licence or terms.",
                    },
                    "training_data": {
                        "reason": "unreported",
                        "note": "Not described; the preprint gives only the served model id.",
                    },
                    "checkpoint_revision": {
                        "reason": "unreported",
                        "note": f"Only the served model id {row['model_id']} is printed, with "
                                "no snapshot date or revision, so the record stays at service "
                                "level and is not assigned to a checkpoint.",
                    },
                },
                "provenance_note": (
                    f"Identified only by the served model id {row['model_id']} and the access "
                    f"route {row['access_route']}; kept at service level because no checkpoint "
                    "is named."
                ),
                "review": review(
                    PARSE_METHODS,
                    f"Model id, harness and access route parsed from the Table B1 row with "
                    f"'{row['model_id']}' and the reasoning settings asserted.",
                    method_note=PARSE_REVIEW_NOTE,
                ),
            },
            facets=FACETS_M,
        ))

    # -------------------------------------------------------------- methods
    method_ids = {}
    for harness_text, (hslug, hname, hversion) in HARNESS_SLUGS.items():
        mid = P + "method-" + hslug
        method_ids[hslug] = mid
    for hslug, hname, hversion in sorted({v for v in HARNESS_SLUGS.values()}):
        add(record(
            P + "method-" + hslug, "method", hname, HARNESS_TEXT[hslug],
            {
                "entity_level": "method",
                "reported_name": hname,
                "version": hversion,
                "access": "Agent harness named with its version in Table B1; no repository or "
                          "licence is given in the preprint.",
                "source_locator": f"Table B1, column 'Harness (version)'",
                "missing_metadata": {
                    "parameters": {
                        "reason": "inapplicable",
                        "note": "A harness, not a model; the model it drives is on the "
                                "configuration.",
                    },
                },
                "review": review(
                    PARSE_METHODS,
                    f"'{hname} {hversion}' asserted as the harness string of its Table B1 rows.",
                    method_note=PARSE_REVIEW_NOTE,
                ),
            },
            facets=FACETS_M,
        ))

    # ------------------------------------------------------- configurations
    d2 = t["table_d2"]
    config_ids = {}
    for row in d2:
        system = row["system"]
        effort = row["effort"]
        b1row = b1[system]
        hslug, hname, hversion = HARNESS_SLUGS[b1row["harness"]]
        cid = P + "config-" + SYSTEM_SLUGS[system] + "-" + slug(effort)
        config_ids[(system, effort)] = cid
        proxy = ", with an in-sandbox proxy" if "proxy" in b1row["harness"] else ""
        add(record(
            cid, "configuration", f"{system} in {hname} {hversion}, {effort} reasoning effort",
            f"{system} driven by {hname} {hversion} at {effort} reasoning effort in a Modal "
            f"sandbox with two vCPUs and 6 GiB of memory, a two-hour attempt limit and "
            f"network access restricted to the model provider.",
            {
                "reported_name": system,
                "version": f"{b1row['model_id']} in {hname} {hversion}, {effort} reasoning effort",
                "model_version": b1row["model_id"],
                "configuration_type": "default",
                "hyperparameters": f"Reasoning effort {effort} (the {row['tier']} of this "
                                   f"system's three settings: "
                                   f"{', '.join(b1row['reasoning_settings'])})",
                "environment": {
                    "orchestrator": "Harbor",
                    "sandbox": "Modal, 2 vCPU, 6 GiB memory",
                    "network": "Restricted to calls to the model provider",
                    "attempt_limit": "Two hours per attempt",
                    "access_route": b1row["access_route"],
                    "harness": f"{hname} {hversion}{proxy}",
                },
                "selection": (
                    "Ten attempts per protocol-development task and five per construct-design "
                    "task, at this reasoning setting"
                ),
                "access_reuse": (
                    f"Hosted model over {b1row['access_route']}, driven by {hname} "
                    f"{hversion}. The benchmark harness configuration itself was not "
                    "retrievable: " + ACCESS_GAP
                ),
                "source_locator": f"Section 3.3; Table B1, row '{system}'; Table D2, row "
                                  f"'{system}' tier '{row['tier']}' effort '{effort}'",
                "missing_metadata": {
                    "temperature_note": {
                        "reason": "unreported",
                        "note": "Sampling settings beyond the named reasoning effort are not "
                                "printed.",
                    },
                    "code_commit": {
                        "reason": "unavailable",
                        "note": ACCESS_GAP,
                    },
                },
                "limitations": [
                    "Run by the benchmark's authors, not by the model's developer.",
                    f"Attempts were capped at two hours; Table D1 records "
                    f"{[r for r in t['table_d1'] if r['system'] == system and r['effort'] == effort][0]['cap_hits']}"
                    " time-cap hits for this lane.",
                ],
                "provenance_note": (
                    f"Agent configuration as run in BenchBench-Cloning at the {effort} "
                    "reasoning setting."
                ),
                "review": review(
                    PARSE_METHODS,
                    "Harness, access route and reasoning settings parsed from Table B1 with "
                    "the model id asserted; the lane's tier and effort parsed from Table D2, "
                    "where the three tiers were asserted to appear in the order low, mid, top.",
                    method_note=PARSE_REVIEW_NOTE,
                ),
            },
            facets=FACETS_M,
            links=[
                link("configuration_of", P + "method-" + hslug),
                link("uses_model", model_ids[system]),
            ],
        ))

    # ------------------------------------------------------------ protocols
    e1 = {row["system"]: row for row in t["table_e1"]}
    e2 = {row["system"]: row for row in t["table_e2"]}

    add(record(
        PR_PD, "protocol",
        "BenchBench-Cloning protocol development: single-attempt pass rate over 50 tasks",
        "Each system makes ten independent attempts at each of the 50 protocol-development "
        "tasks; an attempt passes when the cloning simulator executes its protocol and ends "
        "with one isolated product matching the hidden target, and the pass rate is the mean "
        "over a task's ten attempts then over the 50 tasks.",
        {
            "protocol": (
                "The agent receives the scientist's request, the inventory of starting "
                "materials, the documentation for the 42-operation protocol language and "
                "analysis tools, and writes a protocol to an answer file. The protocol is "
                "passed through the cloning simulator and assigned a binary score. Ten "
                "attempts per task, each capped at two hours, in a Modal sandbox with two "
                "vCPUs and 6 GiB of memory and network access restricted to the model "
                "provider. Single-turn: no clarifying questions and no feedback between "
                "attempts."
            ),
            "version": "arXiv:2610.33355v1 Sections 3.1, 3.3 and 3.4",
            "metric": "success-rate",
            "metric_direction": "higher",
            "unit": "percent",
            "metric_qualifier": (
                "protocol-development pass rate at a single attempt (pass@1); simulator-graded, "
                "binary per attempt"
            ),
            "metric_definition": (
                "\"the proportion of attempts whose submitted protocol executes successfully "
                "and produces the isolated target sequence. We average the ten attempt "
                "outcomes within each task and average across the fifty tasks\" (Section 3.4, "
                "quoted)."
            ),
            "denominator": 500,
            "replicates": "Ten attempts per task per system per reasoning setting",
            "bootstrap_replicates": 20000,
            "uncertainty_reporting": {
                "type": "confidence_interval",
                "level": 0.95,
                "method": "bootstrap",
                "resamples": 20000,
                "note": BOOTSTRAP,
            },
            "aggregation": "Mean over a task's ten attempts, then unweighted mean over the 50 tasks",
            "success_threshold": {
                "criterion": "Protocol executes in the simulator and ends with one isolated "
                             "product matching the hidden target sequence",
                "scale": "binary per attempt",
            },
            "control": "Alternative construction routes are accepted when they pass through the "
                       "simulator and produce the same final product as the reference protocol",
            "source_locator": "Sections 3.1, 3.3 and 3.4; Table 2 column 'Protocol dev. %'; "
                              "Table D2 column 'Protocol dev. % [95% CI]'",
            "limitations": [
                SIMULATOR_LIMIT,
                "The stated denominator is 500 attempts (50 tasks x 10), and every printed "
                "pass rate equals the Table E1 passed count divided by 500. For Grok 4.7 and "
                "Gemini 3.8 Flash the Table E1 graded counts are 498 and 496, and Table E2 "
                "records 50 and 4 unscored attempts and 548 recorded attempts for Grok 4.7, so "
                "the paper does not state whether ungraded attempts are counted as failures or "
                "dropped.",
                "Pass rates are reported only at the aggregate level: no per-task value is "
                "printed for this set.",
                "Single-turn by design (Section 6.2).",
            ],
            "review": review(
                PARSE_METHODS,
                "The denominator was checked, not assumed: every printed pass rate equals the "
                "Table E1 passed count over 500, and every value lies on the 1/500 = 0.2-point "
                "grid that a mean of binary outcomes over 500 attempts must occupy.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("part_of", B_PD), link("uses_data", DS_PD)],
    ))

    add(record(
        PR_CD, "protocol",
        "BenchBench-Cloning construct design: single-attempt pass rate over 15 tasks",
        "Each system makes five independent attempts at each of the 15 construct-design "
        "tasks; an attempt passes at a final score of at least 0.9, and the pass rate is the "
        "mean over a task's five attempts then over the 15 tasks.",
        {
            "protocol": (
                "The agent receives the scientific objective, sequence records and supporting "
                "materials, and returns an annotated construct sequence, orderable primers "
                "where required, a construction plan and a written justification. Every task "
                "has a deterministic grader over the returned sequences, their source and the "
                "construction route. On ten of the fifteen tasks the final score is the product "
                "of the deterministic result and a GPT-6 Astra rubric score of the written "
                "reasoning and plan; on the other five it is the deterministic result alone. "
                "An attempt is classified successful at a final score of at least 0.9. Five "
                "attempts per task, each capped at two hours."
            ),
            "version": "arXiv:2610.33355v1 Sections 3.2, 3.3 and 3.4; Appendix A",
            "metric": "success-rate",
            "metric_direction": "higher",
            "unit": "percent",
            "metric_qualifier": (
                "construct-design pass rate at a single attempt; mixed grading, deterministic "
                "on five tasks and deterministic multiplied by a GPT-6 Astra rubric score on "
                "ten, pass at a final score of at least 0.9"
            ),
            "metric_definition": (
                "\"an attempt is classified as successful when its final score is at least "
                "0.9. The pass rate is computed by averaging the five attempt outcomes within "
                "each task and then averaging across the 15 tasks\" (Section 3.4, quoted)."
            ),
            "denominator": 75,
            "replicates": "Five attempts per task per system per reasoning setting",
            "bootstrap_replicates": 20000,
            "uncertainty_reporting": {
                "type": "confidence_interval",
                "level": 0.95,
                "method": "bootstrap",
                "resamples": 20000,
                "note": BOOTSTRAP,
            },
            "aggregation": "Mean over a task's five attempts, then unweighted mean over the 15 tasks",
            "success_threshold": {
                "criterion": "Final score of at least 0.9, where the final score is the "
                             "deterministic grader's result, multiplied on ten tasks by the "
                             "rubric judge's score",
                "scale": "0 to 1",
                "threshold": "0.9",
            },
            "source_locator": "Sections 3.2, 3.3 and 3.4; Appendix A; Table 2 column 'Construct "
                              "design %'; Table D2 column 'Construct design % [95% CI]'",
            "limitations": [
                "Two grading kinds are pooled in this one rate: deterministic-only on five "
                "tasks and deterministic multiplied by a model judge on ten. The per-task "
                "protocols keep them apart; this aggregate does not.",
                "GPT-6 Astra is the rubric judge and is also one of the eight evaluated "
                "systems; no self-preference analysis is reported.",
                "Table F1 records that the shipped grader result was revised for 48 of the 600 "
                "top-effort trials, so these rates embed a manual adjudication pass.",
                SIMULATOR_LIMIT,
                "Five attempts per task over 15 tasks give wide intervals: every printed 95% "
                "interval spans at least 18 percentage points.",
            ],
            "review": review(
                PARSE_METHODS,
                "The denominator was checked, not assumed: for each system the Table G2 "
                "per-task solve counts sum to the numerator of the printed rate over 75 "
                "attempts (15 tasks x 5) in all eight top-effort lanes. One value in the wider "
                "Table D2, Gemini 4 Argon at low effort, does not lie on the 1/75 grid; it is "
                "recorded with that anomaly on the result.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("part_of", B_CD), link("uses_data", DS_CD)],
    ))

    add(record(
        PR_AGG, "protocol",
        "BenchBench-Cloning aggregate score over all 65 tasks",
        "Task-weighted mean of a system's protocol-development and construct-design "
        "single-attempt pass rates, weighted 50/65 and 15/65 so that each of the 65 tasks "
        "counts equally.",
        {
            "protocol": (
                "Computed from the two single-attempt pass rates of the same system at the "
                "same reasoning setting; it is not a separate run. Weights are 50/65 for "
                "protocol development and 15/65 for construct design."
            ),
            "version": "arXiv:2610.33355v1 Section 3.4",
            "metric": "success-rate",
            "metric_direction": "higher",
            "unit": "percent",
            "metric_qualifier": (
                "aggregate single-attempt score over all 65 tasks, task-weighted 50/65 "
                "protocol development and 15/65 construct design; printed as 'Aggregate %' in "
                "Tables 2 and D2 and as 'Aggregate accuracy (%)' in Figures 2 and 5"
            ),
            "metric_definition": (
                "\"The aggregate score is a weighted average of the protocol-development and "
                "construct-design scores, with weights of 50/65 and 15/65, respectively, "
                "giving each task equal weight\" (Section 3.4, quoted)."
            ),
            "denominator": 575,
            "aggregation": "Weighted mean of the two task-set pass rates, weights 50/65 and 15/65",
            "bootstrap_replicates": 20000,
            "uncertainty_reporting": {
                "type": "confidence_interval",
                "level": 0.95,
                "method": "bootstrap",
                "resamples": 20000,
                "note": BOOTSTRAP,
            },
            "source_locator": "Section 3.4; Table 2 column 'Aggregate %'; Table D2 column "
                              "'Aggregate % [95% CI]'",
            "limitations": [
                "A derived composite of two rates measured with different graders, different "
                "attempt counts per task (ten against five) and different grading kinds; it is "
                "not itself a measurement.",
                "The denominator 575 counts attempts, not tasks: 500 protocol-development "
                "attempts plus 75 construct-design attempts. The weights are over tasks "
                "(50/65 and 15/65), which the paper states.",
                "Carries every limitation of both component rates, including the model judge on "
                "ten construct-design tasks.",
            ],
            "review": review(
                PARSE_METHODS,
                "Every one of the 24 printed aggregates was recomputed from the printed "
                "component rates as (50 x protocol + 15 x construct) / 65 and agrees to within "
                "0.05 points, the residue of rounding the inputs; the largest residue is "
                "GPT-6.1 Sol at max effort, where the inputs give 22.15 and the table prints "
                "22.2.",
                method_note=PARSE_REVIEW_NOTE,
            ),
        },
        links=[link("part_of", B_SUITE), link("uses_data", DS_PD)],
    ))

    for pid, k, label in ((PR_P5, 5, "five"), (PR_P10, 10, "ten")):
        add(record(
            pid, "protocol",
            f"BenchBench-Cloning protocol development: pass@{k} over 50 tasks",
            f"Probability that at least one of {label} attempts at a protocol-development "
            f"task passes the cloning simulator, estimated from the ten recorded attempts per "
            f"task and averaged over the 50 tasks.",
            {
                "protocol": (
                    f"Derived from the same ten recorded attempts per task as the "
                    f"single-attempt pass rate. pass@{k} estimates the probability that at "
                    f"least one of {k} attempts succeeds, which the paper reports as an upper "
                    "bound on single-system performance because a scientist can compare "
                    "several candidate answers before acting on one. It is a best-of-k "
                    "quantity and is not a single-attempt performance measure."
                ),
                "version": "arXiv:2610.33355v1 Sections 3.4 and 4.2; Appendix G",
                "metric": "success-rate",
                "metric_direction": "higher",
                "unit": "percent",
                "metric_qualifier": (
                    f"protocol-development pass@{k}: probability that at least one of {k} "
                    "attempts passes; best-of-k, never comparable with single-attempt pass rate"
                ),
                "metric_definition": (
                    "\"we additionally report pass@k for up to ten attempts to measure the "
                    "probability that at least one of k attempts succeeds. This measures the "
                    "availability of a valid protocol among repeated attempts\" (Section 3.4, "
                    "quoted)."
                ),
                "denominator": 500,
                "replicates": "Ten recorded attempts per task; pass@k estimated from them",
                "bootstrap_replicates": 20000,
                "uncertainty_reporting": {
                    "type": "confidence_interval",
                    "level": 0.95,
                    "method": "bootstrap",
                    "resamples": 20000,
                    "note": "Table G1's intervals use the same bootstrap draws as Table 2 "
                            "(Appendix G). " + BOOTSTRAP,
                },
                "aggregation": f"pass@{k} per task, then unweighted mean over the 50 tasks",
                "source_locator": f"Sections 3.4 and 4.2; Table G1 column 'pass@{k} % [95% CI]'",
                "limitations": [
                    "A best-of-k upper bound, not achievable performance: the authors note its "
                    "practical value depends on identifying the valid solution among the "
                    "candidates, and that they did not evaluate a selection procedure "
                    "(Section 6.1).",
                    "System ranking is not stable in k: Claude Opus 5.5 beats GPT-6.1 Sol at "
                    "k = 1 and loses to it at k = 10 (Section 4.2).",
                    "Grok 4.7 and Gemini 3.8 Flash have a k = 9 cap on 2 and 4 tasks "
                    "respectively (Table G1 note), so their pass@10 rests on fewer than ten "
                    "attempts for those tasks. The paper does not say how the estimate handles "
                    "the shortfall.",
                    "The estimator is not printed: the paper does not say whether pass@k is the "
                    "unbiased combinatorial estimator or an empirical resample.",
                ],
                "review": review(
                    PARSE_METHODS,
                    "Table G1 was parsed with every row label asserted, and pass@1 was asserted "
                    "to repeat the Table 2 protocol-development column exactly, which ties this "
                    "table to the same runs.",
                    method_note=PARSE_REVIEW_NOTE,
                ),
            },
            links=[link("part_of", B_PD), link("uses_data", DS_PD)],
        ))

    for pid, column, phrase in (
        (PR_SOLVED1, "Solved >=1",
         "solved at least once in the ten recorded attempts"),
        (PR_SOLVEDALL, "Solved all",
         "solved in every one of the ten recorded attempts"),
    ):
        add(record(
            pid, "protocol",
            f"BenchBench-Cloning protocol development: tasks {phrase}, out of 50",
            f"Number of the 50 protocol-development tasks that a system {phrase}, counted at "
            f"its top reasoning setting.",
            {
                "protocol": (
                    "A coverage count over the same ten recorded attempts per task as the "
                    "single-attempt pass rate, at the top reasoning setting only. Counts "
                    "tasks, not attempts."
                ),
                "version": "arXiv:2610.33355v1 Section 4.2; Appendix G",
                "metric": "count",
                "metric_direction": "higher",
                "unit": "count",
                "unit_detail": "protocol-development tasks, out of 50",
                "metric_qualifier": (
                    f"protocol-development tasks {phrase}, out of 50; a coverage count under "
                    "repeated sampling, not a single-attempt performance measure"
                ),
                "denominator": 50,
                "aggregation": "Count of tasks over the 50-task set",
                "source_locator": f"Table G1, column '{column}'",
                "limitations": [
                    "A best-of-ten coverage count, not single-attempt performance.",
                    "No interval is printed for either count.",
                    "Reported only at the top reasoning setting.",
                    "Grok 4.7 and Gemini 3.8 Flash have a k = 9 cap on 2 and 4 tasks "
                    "respectively (Table G1 note).",
                ],
                "review": review(
                    PARSE_METHODS,
                    "Each system's 'Solved >=1' count was checked against its printed pass@10: "
                    "the count over 50 equals pass@10 for all eight systems.",
                    method_note=PARSE_REVIEW_NOTE,
                ),
            },
            links=[link("part_of", B_PD), link("uses_data", DS_PD)],
        ))

    for pid, judged, tasks, subset in (
        (PR_TASK_DET, False, det_tasks, DS_CD_DET),
        (PR_TASK_JUDGED, True, judged_tasks, DS_CD_JUDGED),
    ):
        add(record(
            pid, "protocol",
            "BenchBench-Cloning construct design, per task: attempts passed out of 5, "
            + ("deterministic grading with a rubric model judge" if judged
               else "deterministic grading only"),
            "Attempts passed out of five on a single construct-design task, counted at the "
            "top reasoning setting, where the attempt is graded "
            + ("by a deterministic check whose result is multiplied by a GPT-6 Astra rubric "
               "score of the written reasoning and plan, and passes at a final score of at "
               "least 0.9."
               if judged else
               "by a task-specific deterministic check of the returned sequences, their "
               "source and the construction route, and passes at a final score of at least "
               "0.9."),
            {
                "protocol": (
                    "Five attempts per task at the top reasoning setting. "
                    + ("The final score is the product of the deterministic grader's result "
                       "and the rubric judge's score, so a submission that clears the "
                       "deterministic checks can still fail: Table F3 records 34 such "
                       "attempts of 142 across the eight systems."
                       if judged else
                       "The final score is the deterministic grader's result alone; no model "
                       "judge is involved.")
                ),
                "version": "arXiv:2610.33355v1 Section 3.2; Appendix A; Appendix G",
                "metric": "count",
                "metric_direction": "higher",
                "unit": "count",
                "unit_detail": "attempts passed, out of 5",
                "metric_qualifier": (
                    "construct-design attempts passed out of 5 on one task at top reasoning "
                    "effort, pass at a final score of at least 0.9; grading "
                    + ("deterministic multiplied by a GPT-6 Astra rubric score, so the outcome "
                       "depends on the judge" if judged else "deterministic only, no model judge")
                ),
                "denominator": 5,
                "replicates": "Five attempts per task per system",
                "aggregation": "None: the count is per task and per system",
                "success_threshold": {
                    "criterion": "Final score of at least 0.9",
                    "scale": "0 to 1",
                    "threshold": "0.9",
                },
                "source_locator": "Table G2 rows for the "
                                  + ("ten rubric-judged" if judged else "five deterministic-only")
                                  + " tasks; Table A1 column 'Grading'",
                "limitations": [
                    "Five attempts give a count on a six-point scale with no interval; the "
                    "paper prints none.",
                    "Reported only at the top reasoning setting.",
                ] + ([
                    "The judge is GPT-6 Astra, which is also one of the eight evaluated "
                    "systems.",
                    "Table F1 records manual re-adjudication of grader results, and Table F2 "
                    "lists reviewed attempts whose deterministic verdict changed.",
                ] if judged else []),
                "review": review(
                    PARSE_METHODS,
                    "Each task row of Table G2 was parsed with its label asserted and all "
                    "eight cells read in one regex, so a cell cannot be taken from a "
                    "neighbouring column. Figure 6 prints the same 120 cells; the parser "
                    "searches only the lines between the Table G1 caption and the Table G2 "
                    "caption, so the figure cannot be read instead.",
                    method_note=PARSE_REVIEW_NOTE,
                ),
            },
            links=[link("part_of", B_CD), link("uses_data", subset)]
                  + [link("evaluates_task", task_ids[name]) for name in tasks],
        ))

    # ---------------------------------------------- evaluations and results
    def comparison(protocol_id, population, inputs, adaptation, metric_impl,
                   aggregation, budget, dataset_version, split):
        return {
            "protocol_id": protocol_id,
            "dataset_version": dataset_version,
            "split": split,
            "population": population,
            "inputs": inputs,
            "adaptation": adaptation,
            "metric_implementation": metric_impl,
            "aggregation": aggregation,
            "budget": budget,
        }

    BUDGET = ("Modal sandbox, 2 vCPU and 6 GiB memory, network restricted to the model "
              "provider, two hours per attempt")
    PD_INPUTS = ("Scientist's request, inventory of up to eight starting plasmids as GenBank "
                 "or FASTA with annotations and material-property notes, documentation for the "
                 "42-operation protocol language, and analysis tools (Python, Biopython, "
                 "Primer3-py, plotting libraries)")
    CD_INPUTS = ("Scientist's objective, sequence records and supporting materials; for six "
                 "tasks also experimental records from the source study")
    ADAPT = ("Single-turn agent attempt: the agent inspects the supplied files, uses the "
             "available tools, revises within the attempt and writes its submission to a "
             "designated answer file; no clarifying questions and no feedback between attempts")

    def evaluation(eid, name, system_id, assessment_id, data_id, comp, locator,
                   coverage=None, missing=None, limitations=None, n_runs=None,
                   denominator=None):
        attrs = {
            "origin": "author_reported",
            "protocol": comp["protocol_id"],
            "version": "arXiv:2610.33355v1 as retrieved 2026-11-06",
            "comparison": comp,
            "source_locator": locator,
        }
        if n_runs is not None:
            attrs["n_runs"] = n_runs
        if denominator is not None:
            attrs["denominator"] = denominator
        if coverage is not None:
            attrs["coverage"] = coverage
        if missing:
            attrs["missing_metadata"] = missing
        attrs["limitations"] = (limitations or []) + [
            "Reported by the benchmark's authors, who also built the benchmark and ran every "
            "system on it.",
            "Not reproduced by Rewire: " + ACCESS_GAP,
        ]
        attrs["review"] = review(
            PARSE_METHODS,
            "Transcribed from the pinned preprint by extract/parse_tables.py; not rerun.",
            method_note=PARSE_REVIEW_NOTE,
        )
        return record(
            eid, "evaluation", name, NOT_REPRODUCED, attrs,
            links=[
                link("system", system_id),
                link("assessment", assessment_id),
                link("data", data_id),
            ],
        )

    def result(rid, name, eval_id, metric, direction, unit, printed, numeric,
               qualifier, locator, uncertainty=None, missing=None, unit_detail=None,
               coverage=None, denominator=None, numerator=None, extra=None,
               note=None, anomaly=None):
        attrs = {
            "metric": metric,
            "metric_qualifier": qualifier,
            "metric_direction": direction,
            "unit": unit,
            "printed_value": printed,
            "numeric_value": numeric,
            "source_locator": locator,
        }
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        if denominator is not None:
            attrs["denominator"] = denominator
        if numerator is not None:
            attrs["numerator"] = numerator
        if coverage is not None:
            attrs["coverage"] = coverage
        if uncertainty is not None:
            attrs["uncertainty"] = uncertainty
        if missing:
            attrs["missing_metadata"] = missing
        if anomaly:
            attrs["source_anomaly"] = anomaly
        if extra:
            attrs.update(extra)
        attrs["review"] = review(
            PARSE_METHODS,
            note or "Extraction only. " + PARSE_REVIEW_NOTE,
            method_note=PARSE_REVIEW_NOTE,
        )
        return record(
            rid, "result", name, NOT_REPRODUCED, attrs, facets={},
            links=[link("evaluation", eval_id)],
        )

    def interval(cell, printed_cell):
        return {
            "type": "confidence_interval",
            "printed": printed_cell,
            "lower": cell[1],
            "upper": cell[2],
            "level": 0.95,
            "method": "bootstrap",
            "resamples": 20000,
            "unit": "percent",
            "note": BOOTSTRAP,
        }

    # Table D2: 24 lanes x 3 metrics.
    METRIC_LANES = [
        ("protocol_development", "protocol-development", PR_PD, B_PD, DS_PD,
         "Protocol dev. % [95% CI]", "protocol-development pass rate"),
        ("construct_design", "construct-design", PR_CD, B_CD, DS_CD,
         "Construct design % [95% CI]", "construct-design pass rate"),
        ("aggregate", "aggregate", PR_AGG, B_SUITE, DS_PD,
         "Aggregate % [95% CI]", "aggregate score"),
    ]

    for row in d2:
        system = row["system"]
        effort = row["effort"]
        cfg = config_ids[(system, effort)]
        top = row["tier"] == "top"
        for key, key_slug, protocol_id, assessment_id, data_id, column, metric_name in METRIC_LANES:
            cell = row[key]
            printed_cell = f"{cell[0]} [{cell[1]}, {cell[2]}]"
            eid = f"{P}eval-{SYSTEM_SLUGS[system]}-{slug(effort)}-{key_slug}"
            rid = f"{P}result-{SYSTEM_SLUGS[system]}-{slug(effort)}-{key_slug}"
            locator = (
                f"Table D2, row '{system}' tier '{row['tier']}' effort '{effort}', "
                f"column '{column}'"
            )
            if top:
                locator += (
                    f"; the same cell is printed in Table 2, row '{system}', column "
                    f"'{column.split(' [')[0]}'"
                )

            if key == "protocol_development":
                comp = comparison(
                    protocol_id,
                    "50 protocol-development tasks, ten attempts each",
                    PD_INPUTS, ADAPT,
                    "Binary simulator pass per attempt: executes and ends with one isolated "
                    "product matching the hidden target",
                    "Mean over a task's ten attempts, then unweighted mean over the 50 tasks",
                    BUDGET,
                    "BenchBench-Cloning task corpus as published in arXiv:2610.33355v1",
                    "Evaluation only; all 50 tasks scored",
                )
                n_runs = 10
                denominator = 500
                if top:
                    graded = e1[system]["graded"]
                    passed = e1[system]["passed"]
                    recorded = e2[system]["recorded"]
                    cov = {
                        "scored": graded,
                        "eligible": 500,
                        "unit": "attempts",
                        "note": (
                            f"Table E1 prints {graded} graded attempts and {passed} passed; "
                            f"Table E2 prints {recorded} recorded. The printed pass rate equals "
                            f"{passed}/500."
                        ),
                    }
                    missing = None
                    numerator = passed
                else:
                    cov = None
                    numerator = None
                    missing = {
                        "coverage": {
                            "reason": "unreported",
                            "note": "Tables E1 and E2 give graded and recorded attempt counts "
                                    "at top effort only, so the number of attempts actually "
                                    "graded in this lane is not printed.",
                        },
                    }
                lane_limits = []
                if top and e1[system]["graded"] != 500:
                    lane_limits.append(
                        f"Table E1 grades {e1[system]['graded']} of the 500 attempts for this "
                        f"system and Table E2 records {e2[system]['recorded']} recorded with "
                        f"{e2[system]['unscored']} unscored; the printed rate uses 500 as the "
                        "denominator, which the paper does not state."
                    )
            elif key == "construct_design":
                comp = comparison(
                    protocol_id,
                    "15 construct-design tasks, five attempts each",
                    CD_INPUTS, ADAPT,
                    "Final score of at least 0.9, where the final score is the deterministic "
                    "grader's result on five tasks and the product of the deterministic result "
                    "and a GPT-6 Astra rubric score on ten",
                    "Mean over a task's five attempts, then unweighted mean over the 15 tasks",
                    BUDGET,
                    "BenchBench-Cloning task corpus as published in arXiv:2610.33355v1",
                    "Evaluation only; all 15 tasks scored",
                )
                n_runs = 5
                denominator = 75
                numerator = None
                cov = {"scored": 75, "eligible": 75, "unit": "attempts",
                       "note": "15 tasks x 5 attempts."}
                missing = None
                lane_limits = [
                    "Pools two grading kinds: deterministic only on five tasks, deterministic "
                    "multiplied by a GPT-6 Astra rubric score on ten.",
                ]
                if top:
                    solved = sum(x["solves"][system] for x in t["table_g2"])
                    cov["note"] = (
                        f"15 tasks x 5 attempts. The Table G2 per-task solve counts for this "
                        f"system sum to {solved}, and {solved}/75 reproduces the printed rate."
                    )
                    numerator = solved
            else:
                comp = comparison(
                    protocol_id,
                    "All 65 tasks: 50 protocol-development with ten attempts each and 15 "
                    "construct-design with five",
                    PD_INPUTS + ". " + CD_INPUTS, ADAPT,
                    "Weighted mean of the two task-set pass rates, weights 50/65 and 15/65",
                    "Task-weighted mean of the protocol-development and construct-design pass "
                    "rates, weights 50/65 and 15/65",
                    BUDGET,
                    "BenchBench-Cloning task corpus as published in arXiv:2610.33355v1",
                    "Evaluation only; all 65 tasks scored",
                )
                n_runs = None
                denominator = 575
                numerator = None
                cov = {"scored": 575, "eligible": 575, "unit": "attempts",
                       "note": "500 protocol-development attempts plus 75 construct-design "
                               "attempts; the weights are over tasks, 50/65 and 15/65."}
                missing = None
                lane_limits = [
                    "A derived composite of the two task-set rates, not a separate measurement.",
                ]

            add(evaluation(
                eid,
                f"{system} at {effort} effort on BenchBench-Cloning {metric_name}",
                cfg, assessment_id, data_id, comp, locator,
                coverage=cov, missing=missing, limitations=lane_limits,
                n_runs=n_runs, denominator=denominator,
            ))

            anomaly = None
            extra = None
            if system == "Gemini 4 Argon" and effort == "low" and key == "construct_design":
                anomaly = (
                    "31.9 is the only pass rate in the paper that does not lie on the grid a "
                    "mean of binary outcomes must occupy. With 15 tasks and five attempts each "
                    "the construct-design rate must be a multiple of 1/75 = 1.333 points; the "
                    "neighbouring grid values are 30.7 (23 passes) and 32.0 (24 passes). The "
                    "printed 95% interval [10.7, 52.0] is also identical to this system's "
                    "top-effort interval in the row below. Stored as printed."
                )
                extra = {
                    "source_warnings": [
                        "Off-grid value: not a multiple of 1/75, so it cannot be a mean of "
                        "five binary outcomes over 15 tasks.",
                        "Printed 95% interval is byte-identical to the same system's "
                        "top-effort interval.",
                    ],
                }

            add(result(
                rid,
                f"{system} at {effort} effort, BenchBench-Cloning {metric_name}",
                eid, "success-rate", "higher", "percent",
                cell[0], cell[0],
                (
                    "protocol-development pass rate at a single attempt (pass@1), "
                    "simulator-graded and binary per attempt; "
                    if key == "protocol_development" else
                    "construct-design pass rate at a single attempt, pass at a final score of "
                    "at least 0.9, deterministic grading on five tasks and deterministic "
                    "multiplied by a GPT-6 Astra rubric score on ten; "
                    if key == "construct_design" else
                    "aggregate single-attempt score over all 65 tasks, task-weighted 50/65 "
                    "protocol development and 15/65 construct design; "
                ) + f"{effort} reasoning effort ({row['tier']} of this system's three settings)",
                locator,
                uncertainty=interval(cell, printed_cell),
                coverage=cov,
                denominator=denominator,
                numerator=numerator,
                extra=extra,
                anomaly=anomaly,
                note=(
                    "Extraction only. Parsed from the Table D2 row with the system label, "
                    "tier and effort asserted and all eight numbers of the row read in one "
                    "regex, so a value cannot be taken from a neighbouring column. "
                    + (
                        "Figures 2, 3 and 5 print the same aggregate and task-set numbers; the "
                        "parser searches only the lines between the Table D1 caption and the "
                        "Table D2 caption, so a figure label cannot be read instead. "
                        if True else ""
                    )
                    + PARSE_REVIEW_NOTE
                ),
            ))

    # Table G1: pass@5, pass@10, solved counts. Top effort only.
    top_effort = {row["system"]: row["effort"] for row in d2 if row["tier"] == "top"}
    for row in t["table_g1"]:
        system = row["system"]
        effort = top_effort[system]
        cfg = config_ids[(system, effort)]
        for key, k, pid in (("pass_at_5", 5, PR_P5), ("pass_at_10", 10, PR_P10)):
            cell = row[key]
            printed_cell = f"{cell[0]} [{cell[1]}, {cell[2]}]"
            eid = f"{P}eval-{SYSTEM_SLUGS[system]}-pass-at-{k}"
            rid = f"{P}result-{SYSTEM_SLUGS[system]}-pass-at-{k}"
            locator = f"Table G1, row '{system}', column 'pass@{k} % [95% CI]'"
            comp = comparison(
                pid,
                "50 protocol-development tasks, ten recorded attempts each",
                PD_INPUTS, ADAPT,
                f"pass@{k}: probability that at least one of {k} attempts passes the simulator",
                f"pass@{k} per task, then unweighted mean over the 50 tasks",
                BUDGET,
                "BenchBench-Cloning task corpus as published in arXiv:2610.33355v1",
                "Evaluation only; all 50 tasks scored",
            )
            note = row["note"].strip()
            add(evaluation(
                eid, f"{system} on BenchBench-Cloning protocol development, pass@{k}",
                cfg, B_PD, DS_PD, comp, locator,
                coverage={
                    "scored": e1[system]["graded"], "eligible": 500, "unit": "attempts",
                    "note": f"Derived from the same recorded attempts as the single-attempt "
                            f"rate; Table E1 prints {e1[system]['graded']} graded of 500."
                            + (f" Table G1 notes a {note} for this system." if note else ""),
                },
                n_runs=10, denominator=500,
                limitations=[
                    f"Best-of-{k} upper bound, not single-attempt performance; never comparable "
                    "with the pass rate.",
                ] + ([f"Table G1 records a {note} for this system, so some tasks rest on fewer "
                      "than ten attempts."] if note else []),
            ))
            add(result(
                rid, f"{system}, BenchBench-Cloning protocol-development pass@{k}",
                eid, "success-rate", "higher", "percent", cell[0], cell[0],
                f"protocol-development pass@{k}: probability that at least one of {k} attempts "
                f"passes; best-of-k, never comparable with single-attempt pass rate; "
                f"{effort} reasoning effort",
                locator,
                uncertainty=interval(cell, printed_cell),
                denominator=500,
                extra=({"source_warnings": [
                    f"Table G1 records a {note} for this system: some tasks have fewer than ten "
                    "attempts, and the paper does not say how pass@k handles the shortfall."
                ]} if note else None),
                note="Extraction only. Parsed from the Table G1 row with the system label "
                     "asserted and all eleven numbers of the row read in one regex. pass@1 in "
                     "the same row was asserted to equal the Table 2 protocol-development "
                     "value, which ties this table to the same runs. " + PARSE_REVIEW_NOTE,
            ))

        for key, column, pid, phrase in (
            ("solved_at_least_once", "Solved >=1", PR_SOLVED1,
             "solved at least once in ten attempts"),
            ("solved_all", "Solved all", PR_SOLVEDALL,
             "solved in every one of ten attempts"),
        ):
            value = row[key]
            eid = f"{P}eval-{SYSTEM_SLUGS[system]}-{slug(key.replace('_', '-'))}"
            rid = f"{P}result-{SYSTEM_SLUGS[system]}-{slug(key.replace('_', '-'))}"
            locator = f"Table G1, row '{system}', column '{column}'"
            comp = comparison(
                pid,
                "50 protocol-development tasks, ten recorded attempts each",
                PD_INPUTS, ADAPT,
                f"Count of tasks {phrase}",
                "Count over the 50-task set",
                BUDGET,
                "BenchBench-Cloning task corpus as published in arXiv:2610.33355v1",
                "Evaluation only; all 50 tasks scored",
            )
            add(evaluation(
                eid,
                f"{system} on BenchBench-Cloning protocol development, tasks {phrase}",
                cfg, B_PD, DS_PD, comp, locator,
                coverage={"scored": 50, "eligible": 50, "unit": "tasks"},
                n_runs=10, denominator=50,
                limitations=["A coverage count under repeated sampling, not single-attempt "
                             "performance."],
            ))
            add(result(
                rid, f"{system}, BenchBench-Cloning protocol-development tasks {phrase}",
                eid, "count", "higher", "count", str(value), str(value),
                f"protocol-development tasks {phrase}, out of 50; a coverage count under "
                f"repeated sampling, not a single-attempt performance measure; {effort} "
                "reasoning effort",
                locator,
                unit_detail="protocol-development tasks, out of 50",
                denominator=50,
                coverage={"scored": 50, "eligible": 50, "unit": "tasks"},
                missing={"uncertainty": {
                    "reason": "unreported",
                    "note": "Table G1 prints no interval for the solved-task counts.",
                }},
                note="Extraction only. Parsed from the Table G1 row with the system label "
                     "asserted; the 'Solved >=1' count over 50 was checked to equal the "
                     "printed pass@10 for every system. " + PARSE_REVIEW_NOTE,
            ))

    # Table G2: 15 tasks x 8 systems, top effort.
    for task_row in t["table_g2"]:
        name = task_row["task"]
        judged = "rubric" in a1[name]["grading"]
        pid = PR_TASK_JUDGED if judged else PR_TASK_DET
        subset = DS_CD_JUDGED if judged else DS_CD_DET
        tslug = slug(name)
        for system, value in task_row["solves"].items():
            effort = top_effort[system]
            cfg = config_ids[(system, effort)]
            eid = f"{P}eval-{SYSTEM_SLUGS[system]}-task-{tslug}"
            rid = f"{P}result-{SYSTEM_SLUGS[system]}-task-{tslug}"
            locator = f"Table G2, row '{name}', column '{system}'"
            comp = comparison(
                pid,
                f"One construct-design task ('{name}'), five attempts",
                CD_INPUTS, ADAPT,
                ("Final score of at least 0.9, the deterministic grader's result multiplied by "
                 "a GPT-6 Astra rubric score of the written reasoning and plan"
                 if judged else
                 "Final score of at least 0.9 from the task's deterministic grader alone"),
                "None: the count is per task and per system",
                BUDGET,
                "BenchBench-Cloning task corpus as published in arXiv:2610.33355v1",
                "Evaluation only; this one task scored",
            )
            add(evaluation(
                eid,
                f"{system} on BenchBench-Cloning construct design: {name}",
                cfg, task_ids[name], subset, comp, locator,
                coverage={"scored": 5, "eligible": 5, "unit": "attempts"},
                n_runs=5, denominator=5,
                limitations=(
                    ["Graded in part by GPT-6 Astra as a rubric judge, which is also one of the "
                     "eight evaluated systems."] if judged else []
                ) + ["Top reasoning setting only; the paper prints no per-task counts for the "
                     "lower settings."],
            ))
            add(result(
                rid, f"{system}, BenchBench-Cloning construct design: {name}",
                eid, "count", "higher", "count", f"{value}/5", str(value),
                "construct-design attempts passed out of 5 on one task at top reasoning "
                "effort, pass at a final score of at least 0.9; grading "
                + ("deterministic multiplied by a GPT-6 Astra rubric score, so the outcome "
                   "depends on the judge" if judged else
                   "deterministic only, no model judge")
                + f"; {effort} reasoning effort",
                locator,
                unit_detail="attempts passed, out of 5",
                denominator=5, numerator=value,
                coverage={"scored": 5, "eligible": 5, "unit": "attempts"},
                missing={"uncertainty": {
                    "reason": "unreported",
                    "note": "Table G2 prints no interval for the per-task counts.",
                }},
                note="Extraction only. Parsed from the Table G2 row with the task label "
                     "asserted and all eight cells read in one regex, so a cell cannot be taken "
                     "from a neighbouring column. Figure 6 prints the same 120 cells in the "
                     "same x/5 form, which makes a value-level match weak evidence; the parser "
                     "searches only the lines between the Table G1 caption and the Table G2 "
                     "caption, so the figure cannot be read instead. Each system's column was "
                     "summed and checked against its printed construct-design pass rate over "
                     "75 attempts. " + PARSE_REVIEW_NOTE,
            ))

    # ---------------------------------------------------------------- claims
    def claim(cid, name, subject, field, value, locator, sources=None,
              rationale=None, limitations=None, note=None):
        attrs = {
            "field": field,
            "value": value,
            "source_locator": locator,
        }
        if rationale:
            attrs["rationale"] = rationale
        if limitations:
            attrs["limitations"] = limitations
        attrs["review"] = review(
            PARSE_METHODS if note is None else ["pdf-text-parse", "source-hash-verification"],
            note or ("Extraction only. " + PARSE_REVIEW_NOTE),
            method_note=PARSE_REVIEW_NOTE,
        )
        return record(
            cid, "claim", name,
            "Descriptive fact transcribed from the pinned source with its own locator.",
            attrs, facets={},
            sources=sources or [S_PAPER],
            links=[link("subject", subject)],
        )

    # Table 1: family shares.
    for family in t["table_1"]:
        add(claim(
            P + "claim-table1-" + family["slug"] + "-share",
            f"Share of protocol-development tasks: {family['label'].rstrip()}",
            P + "data-family-" + family["slug"],
            "share_of_protocol_development_tasks",
            f"{family['share_percent']}%",
            f"Table 1, row '{family['label'].rstrip()}', column 'Share'",
            rationale=f"{family['tasks']} of the 50 protocol-development tasks. The nine "
                      "shares sum to 100% and the nine counts to 50.",
        ))

    # Table C1: judge agreement.
    for row in t["table_c1"]:
        base = P + "claim-c1-" + slug(row["slug"])
        for field, value, column in (
            ("judge_agreement_trials_graded", str(row["trials_graded"]), "Trials graded"),
            ("judge_agreement_percent", row["agreement_percent"] + "%", "Agreement"),
            ("judge_agreement_cohens_kappa", row["cohens_kappa"], "Cohen's kappa"),
        ):
            add(claim(
                f"{base}-{slug(field)}",
                f"Claude Mythos 5.1 judge agreement, {row['label']}: {column}",
                EV_AGREE, field, value,
                f"Table C1, row '{row['label']}', column '{column}'",
                rationale=(
                    "Agreement between the Claude Mythos 5.1 judge and the outcomes reported "
                    "in the paper, on the binary pass outcome at a final score of 0.9. Kept as "
                    "a claim about the grading procedure, not as a result: it measures "
                    "agreement between graders, not a system's performance on the benchmark."
                ),
                limitations=[
                    "Covers the 450 construct-design attempts of the first six systems "
                    "evaluated, of which the judge declined to grade 63 under its own safety "
                    "policy; those are excluded, leaving 387 graded trials.",
                    "The authors state that agreement between graders does not establish "
                    "independent scientific validity (Section 6.2).",
                ],
            ))

    # Table F1: adjudication outcomes.
    for row in t["table_f1"]:
        for field, value, column in (
            ("adjudication_top_tier_trials", str(row["top_tier_trials"]),
             "Top-tier trials (8x75)"),
            ("adjudication_all_lane_trials", str(row["all_lanes_trials"]),
             "All 24 lanes (24x75)"),
        ):
            add(claim(
                P + "claim-f1-" + row["slug"] + "-" + slug(column),
                f"Construct-design adjudication outcome '{row['label'].rstrip()}': {column}",
                EV_DET, field, value,
                f"Table F1, row '{row['label'].rstrip()}', column '{column}'",
                rationale=(
                    "Counts of construct-design trials by what review decided about the "
                    "shipped grader result. Kept as a claim about the grading procedure, not a "
                    "result: it records a verdict on the grader, not a system's performance."
                ),
                limitations=[
                    "The totals are 600 top-effort trials and 1800 across all 24 lanes; 48 of "
                    "the 600 and 171 of the 1800 did not stand as shipped, so the reported "
                    "pass rates embed a manual adjudication pass.",
                ],
            ))

    # Table F3: judge threshold per system.
    for row in t["table_f3"]:
        sslug = SYSTEM_SLUGS[row["system"]]
        for field, value, column in (
            ("judged_task_attempts", str(row["attempts_on_judged_tasks"]),
             "Attempts on judged tasks"),
            ("passed_deterministic_checks", str(row["passed_deterministic"]),
             "Passed deterministic checks"),
            ("judge_score_below_threshold", str(row["judge_below_0_9"]),
             "Judge score below 0.9"),
        ):
            add(claim(
                P + "claim-f3-" + sslug + "-" + slug(field),
                f"{row['system']} on the ten rubric-judged tasks: {column}",
                EV_JUDGE, field, value,
                f"Table F3, row '{row['system']}', column '{column}'",
                rationale=(
                    "How many of this system's top-effort attempts on the ten rubric-judged "
                    "construct-design tasks cleared the deterministic checks, and how many of "
                    "those the model judge then scored below the 0.9 pass threshold. Kept as a "
                    "claim about the grading procedure: it quantifies the judge's effect on the "
                    "reported pass rates rather than measuring the system on the benchmark."
                ),
                limitations=[
                    "Across the eight systems, 34 of the 142 attempts that cleared the "
                    "deterministic checks fell below the judge's 0.9 threshold, so passing the "
                    "deterministic gate does not imply a pass.",
                ],
            ))

    for field, value, column in (
        ("judged_task_attempts_total", "400", "Attempts on judged tasks"),
        ("passed_deterministic_checks_total", "142", "Passed deterministic checks"),
        ("judge_score_below_threshold_total", "34", "Judge score below 0.9"),
    ):
        add(claim(
            P + "claim-f3-total-" + slug(field),
            f"All systems on the ten rubric-judged tasks: {column}",
            EV_JUDGE, field, value,
            f"Table F3, row 'Total', column '{column}'",
            rationale="Column total over the eight systems; asserted equal to the sum of the "
                      "eight per-system cells while parsing.",
        ))

    # Table E1: first blocking failure categories.
    E1_COLUMNS = [
        ("graded", "Graded", "attempts_graded"),
        ("passed", "Passed", "attempts_passed"),
        ("primer_design", "Primer design", "first_blocking_failure_primer_design"),
        ("final_tube_not_single_product", "Final tube not single product",
         "first_blocking_failure_not_single_product"),
        ("bench_step_failed", "Bench step failed", "first_blocking_failure_bench_step"),
        ("wrong_sequence", "Wrong sequence", "first_blocking_failure_wrong_sequence"),
        ("parser_rejected", "Parser rejected", "first_blocking_failure_parser_rejected"),
        ("no_protocol", "No protocol", "first_blocking_failure_no_protocol"),
    ]
    for row in t["table_e1"]:
        sslug = SYSTEM_SLUGS[row["system"]]
        for key, column, field in E1_COLUMNS:
            add(claim(
                P + "claim-e1-" + sslug + "-" + slug(key),
                f"{row['system']} protocol-development attempts at top effort: {column}",
                EV_SIM, field, str(row[key]),
                f"Table E1, row '{row['system']}', column '{column}'",
                rationale=(
                    "Attempt counts by the first error that blocked execution, at the top "
                    "reasoning setting. Kept as a claim rather than a result: these are "
                    "diagnostic classifications of failures, not a performance measurement on "
                    "the benchmark. The 'Graded' and 'Passed' cells are the denominator and "
                    "numerator evidence behind the protocol-development pass rate."
                ),
                limitations=[
                    "The simulator reports only the first blocking error, so these categories "
                    "do not establish whether later steps would have succeeded (Section 6.2).",
                    "Failure frequencies depend on the routes models choose; models using PCR "
                    "more often meet primer failures, which the authors say may have skewed the "
                    "primer-design share (Section 6.2).",
                    "Figure E1 prints the same counts as shares of graded attempts.",
                ],
            ))

    # Table E2: execution and grading statuses.
    E2_COLUMNS = [
        ("recorded", "Recorded", "attempts_recorded"),
        ("graded", "Graded", "attempts_graded"),
        ("no_protocol", "No protocol", "attempts_with_no_protocol"),
        ("time_cap", "Time cap", "attempts_hitting_time_cap"),
        ("refused", "Refused", "attempts_refused"),
        ("parser_rejected", "Parser rejected", "attempts_parser_rejected"),
        ("unscored", "Unscored", "attempts_unscored"),
    ]
    for row in t["table_e2"]:
        sslug = SYSTEM_SLUGS[row["system"]]
        for key, column, field in E2_COLUMNS:
            add(claim(
                P + "claim-e2-" + sslug + "-" + slug(key),
                f"{row['system']} protocol-development attempt statuses: {column}",
                EV_SIM, field, str(row[key]),
                f"Table E2, row '{row['system']}', column '{column}'",
                rationale=(
                    "Execution and grading status counts for protocol-development attempts. "
                    "Kept as a claim rather than a result: it is run accounting, not a "
                    "performance measurement. These cells carry the denominator question, "
                    "because Grok 4.7 has 548 recorded attempts against an expected 500 and 50 "
                    "unscored, while the printed pass rate uses 500."
                ),
                limitations=[
                    "The paper does not say which reasoning setting Table E2 covers, nor how "
                    "recorded attempts beyond 500 arise or how unscored attempts enter the "
                    "pass-rate denominator.",
                ],
            ))

    # Figure 7: dual-luciferase panel composition.
    FIG7 = [
        ("reference", "Reference", "39/39", "100% signal, no stop codon"),
        ("frame-0", "Frame 0", "39/39", "readthrough in frame"),
        ("frame-plus-1", "Frame +1", "38/39", "continuation in the +1 frame"),
        ("frame-plus-2", "Frame +2", "38/39", "continuation in the +2 frame"),
        ("control", "Control", "0/39",
         "Firefly made without passing the stop (re-initiation)"),
    ]
    for cslug, construct, printed, measures in FIG7:
        add(claim(
            P + "claim-figure7-" + cslug,
            f"Dual-luciferase frame panel: submitted panels containing the {construct} construct",
            task_ids["Dual-luciferase frame panel"],
            "submitted_panels_containing_construct", printed,
            f"Figure 7, row '{construct}', column 'In submitted panels'",
            rationale=(
                f"Of the 39 submitted panels across the eight systems, {printed.split('/')[0]} "
                f"contained the {construct} construct, which measures {measures}. The digits "
                "are printed in the figure and present in the PDF text layer; they are not read "
                "off the artwork. Kept as a claim because they count construct presence in "
                "submissions, not a system's performance on a benchmark panel."
            ),
            limitations=[
                "The denominator 39 is the number of submitted panels, not 40 attempts (eight "
                "systems x five), and the paper does not say what happened to the missing one.",
                "No system passed this task in any attempt (Table G2), so the counts describe "
                "near misses rather than graded success.",
            ],
        ))

    # Descriptive claims.
    descriptive = [
        (
            "task-count-total", B_SUITE, "task_count", "65",
            "Abstract; Section 1; Section 3",
            "50 protocol-development tasks plus 15 construct-design tasks. The 50 was checked "
            "against the Table 1 total and the 15 against the row counts of Tables A1 and G2.",
            None,
        ),
        (
            "task-count-protocol-development", B_PD, "task_count", "50",
            "Abstract; Section 3.1; Table 1, row 'Total', column 'Tasks'",
            "Asserted equal to the sum of the nine dominant-constraint family counts in "
            "Table 1.",
            None,
        ),
        (
            "task-count-construct-design", B_CD, "task_count", "15",
            "Abstract; Section 3.2; Table A1; Table G2",
            "Asserted equal to the 15 rows of Table A1 and the 15 rows of Table G2, whose task "
            "names were asserted to match.",
            None,
        ),
        (
            "construct-design-model-graded-task-count", B_CD,
            "model_graded_task_count", "10 of 15",
            "Section 3.2; Appendix A, Table A1 column 'Grading'",
            "Ten tasks read 'Deterministic + rubric judge' and five read 'Deterministic'; both "
            "counts were asserted while parsing Table A1. On the ten, the final score is the "
            "product of the deterministic result and the rubric score.",
            ["The judge is GPT-6 Astra, which is also one of the eight evaluated systems."],
        ),
        (
            "construct-design-tasks-with-experimental-records", B_CD,
            "tasks_supplying_experimental_records", "6 of 15",
            "Section 3.2; Table A1 column 'Experimental records supplied'",
            "Tasks 1 to 6 of Table A1 supply records such as sequencing reads, per-well growth "
            "and GFP measurements, gel images, antibody and localisation images, microscopy "
            "panels and published readthrough measurements. Count asserted while parsing, and "
            "matching the Table C1 slice 'Tasks with experimental records (6)'.",
            None,
        ),
        (
            "protocol-language-operations", EV_SIM, "supported_operations", "42",
            "Section 2; Section 3.1",
            "The environment includes documentation for a custom cloning protocol language "
            "supporting 42 operations, covering amplification, partial and complete digestion, "
            "Gibson and Golden Gate assembly, oligonucleotide annealing and ligation, end "
            "modification and CRISPR-based operations.",
            None,
        ),
        (
            "product-length-range", DS_PD, "product_length_range",
            "2.8 kb to 15.2 kb, median 5.4 kb",
            "Section 3.1",
            "Products of the protocol-development tasks are circular plasmids.",
            None,
        ),
        (
            "inventory-size", DS_PD, "starting_materials_per_task",
            "Up to eight starting plasmid constructs",
            "Section 3.1",
            "Supplied as GenBank or FASTA files with sequence annotations and notes of "
            "material properties such as methylation sensitivity, GC-rich regions, end "
            "chemistry, counterselection cassettes and host strain.",
            None,
        ),
        (
            "attempts-per-task", B_SUITE, "attempts_per_task",
            "Ten per protocol-development task and five per construct-design task, at every "
            "reasoning setting",
            "Section 3.3; Appendix B",
            "Eight systems at three reasoning settings each give 24 lanes, 500 "
            "protocol-development attempts and 75 construct-design attempts per lane.",
            None,
        ),
        (
            "attempt-budget", B_SUITE, "attempt_budget",
            "Two hours per attempt, in a Modal sandbox with two vCPUs and 6 GiB of memory and "
            "network access restricted to the model provider, orchestrated with Harbor",
            "Section 3.3; Appendix B",
            None,
            None,
        ),
        (
            "systems-evaluated", B_SUITE, "systems_evaluated", "8",
            "Section 3.3; Table B1; Table 2",
            "Claude Opus 5.5, Claude Mythos 5.1, GPT-6 Astra, GPT-6.1 Sol, Gemini 3.8 Flash, "
            "Gemini 4 Argon, Grok 4.7 and Kimi K3, each in its native agent harness where "
            "available and Kimi K3 in the Pi harness.",
            None,
        ),
        (
            "benchmark-unsaturated", B_PD, "saturation",
            "Not saturated within ten attempts: the strongest system leaves 14 of the 50 "
            "protocol-development tasks unsolved",
            "Abstract; Section 4.2; Section 7",
            "GPT-6 Astra solves 36 of 50 tasks at least once in ten attempts (Table G1), so 14 "
            "remain unsolved.",
            None,
        ),
        (
            "licence", B_SUITE, "licence", LICENCE_NOTE,
            "arXiv abstract page licence link; footnote 1 (page 3)",
            None,
            ["The code and data licence is unverified and stays so until the repository or "
             "another authoritative artifact can be retrieved."],
        ),
        (
            "code-and-data-access", D_TASKS, "access", ACCESS_GAP,
            "Footnote 1 (page 3); GitHub web page and API checked 2026-11-06T11:51:23Z",
            "Rechecked at extraction time. The repository is not renamed or moved: a GitHub "
            "repository search for 'benchbench-cloning' returned no results and the repository "
            "is absent from benchling's public repositories.",
            ["The dataset is not marked openly downloadable and no evaluation is marked "
             "reproduced."],
        ),
        (
            "protocol-development-task-release", B_PD, "data_release",
            "Not offered for download: footnote 1 names only the construct-design tasks, "
            "graders and reference solutions",
            "Footnote 1 (page 3)",
            "The protocol-development tasks, their hidden target sequences and the cloning "
            "simulator are not offered for download anywhere in the preprint, so even a working "
            "repository would not make this set reproducible.",
            None,
        ),
        (
            "wet-lab-validation", B_SUITE, "measurement_scope",
            "Simulated and retrospectively graded planning only; no measured laboratory success",
            "Section 6.2",
            "The authors state the benchmark does not directly measure whether models improve "
            "experimental outcomes at the bench, and that the simulator cannot capture every "
            "source of variation in reagents, handling, growth or reaction outcomes.",
            None,
        ),
        (
            "judge-identity", EV_JUDGE, "judge_model", "GPT-6 Astra",
            "Section 3.3",
            "\"GPT-6 Astra served as the model judge for the ten construct-design tasks "
            "requiring rubric-based evaluation\" (quoted). The judge is also one of the eight "
            "evaluated systems.",
            ["No analysis of self-preference by the judge is reported.",
             "Model grading is stochastic and the authors record occasional grading "
             "inconsistency (Section 6.2)."],
        ),
        (
            "judge-second-grader", EV_AGREE, "second_judge_model", "Claude Mythos 5.1",
            "Section 3.3; Appendix C",
            "Every construct-design attempt from the first six systems evaluated was graded a "
            "second time by Claude Mythos 5.1 acting as an independent judge, which saw the "
            "public task text, the private reference material and the submission files but not "
            "the reported outcome.",
            ["It declined to grade 63 of the 450 attempts under its own safety policy; those "
             "are excluded, leaving 387 graded trials."],
        ),
        (
            "pass-threshold", B_CD, "pass_threshold",
            "Final score of at least 0.9", "Section 3.4; Appendix A",
            "On the ten rubric-judged tasks the final score is the product of the deterministic "
            "grader's result and the rubric score, so a submission that clears the "
            "deterministic checks can still fall below the threshold.",
            None,
        ),
        (
            "ranking-not-stable-in-k", PR_P10, "ranking_stability",
            "System ranking is not stable in k: Claude Opus 5.5 beats GPT-6.1 Sol at a single "
            "attempt and loses to it at ten",
            "Section 4.2",
            "The authors attribute this to Opus's successes being concentrated on fewer tasks "
            "while Sol succeeds less consistently across a broader set.",
            None,
        ),
        (
            "sodium-channel-second-construct", task_ids["Sodium-channel promoter repair"],
            "failure_mode",
            "No system ever repaired the second of the two constructs the task requires",
            "Section 5.3; Table G2",
            "GPT-6 Astra and GPT-6.1 Sol fixed the first construct in all of their attempts, "
            "yet no system fixed the second, and no system passed the task in any attempt.",
            None,
        ),
        (
            "matched-panel-overbuild", task_ids["Matched promoter panel"],
            "failure_mode",
            "GPT-6 Astra and GPT-6.1 Sol built an eight-construct factorial panel in every "
            "attempt and so failed the smallest-panel check, while most other systems submitted "
            "the four-construct panel and passed",
            "Section 5.3; Table G2",
            "The task asks for the smallest set of constructs that can resolve a single "
            "discrepancy, and the grader checks for this. It is the one task where the two "
            "strongest systems overall score 0/5 and weaker systems score 5/5.",
            None,
        ),
        (
            "announcement-open-weight-gap", B_SUITE, "announcement_characterisation",
            "The Benchling announcement says Kimi K3's 8.8% highlights the gap between frontier "
            "and open-weight models at this task",
            "Benchling announcement, paragraph beginning 'GPT-6 Astra led with a score of 30.6%'",
            "Recorded because the preprint's Table 2 puts Gemini 3.8 Flash, a hosted frontier "
            "model, at 8.6%, below Kimi K3, so the announcement's framing is not supported by "
            "the paper's own ranking. The source record carries a matching evidence concern "
            "scoped to this claim.",
            ["Withheld from comparison by the evidence concern on the announcement source."],
        ),
    ]
    for cslug, subject, field, value, locator, rationale, limitations in descriptive:
        sources = [S_PAPER]
        note = None
        if cslug == "announcement-open-weight-gap":
            sources = [S_BLOG]
            note = ("Extraction only. Read from the pinned announcement page and compared with "
                    "Table 2 of the preprint.")
        if cslug == "licence":
            sources = [S_PAPER, S_ABS]
        if cslug == "code-and-data-access":
            note = ("Extraction only. Footnote 1 read from the pinned PDF text layer; the "
                    "repository rechecked over HTTP at 2026-11-06T11:51:23Z, returning 404 from "
                    "both the web page and the API, with an empty repository search.")
        add(claim(
            P + "claim-" + cslug,
            f"BenchBench-Cloning: {field.replace('_', ' ')}",
            subject, field, value, locator, sources=sources,
            rationale=rationale, limitations=limitations, note=note,
        ))

    # ------------------------------------------------------------- write out
    ids = [r["id"] for r in records]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    assert not duplicates, f"duplicate IDs: {duplicates}"
    for r in records:
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", r["id"]), f"bad id {r['id']}"

    known = set(ids)
    for r in records:
        for l in r["links"]:
            assert l["target_id"] in known, f"{r['id']} links to unknown {l['target_id']}"
        for sid in r["source_ids"]:
            assert sid in known, f"{r['id']} cites unknown source {sid}"

    records.sort(key=lambda r: r["id"])
    with open(OUT, "w", encoding="utf-8") as handle:
        for r in records:
            handle.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")

    counts = {}
    for r in records:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"wrote {OUT}: {len(records)} records")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
