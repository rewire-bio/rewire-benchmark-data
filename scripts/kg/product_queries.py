"""Named queries for the product questions: ranking, gaps, recipes and provenance (#261).

They read the asserted, inferred and derived graphs and the release graph (release_graph.py),
which holds what the release serves: the evaluations each active relevance judgement rests on,
each use case's baseline methods, and the run receipts. build.py adds QUERIES to the manifest.

rank_for_use_case follows the board rules of the website (rewire-database lib/use-case-comparisons.ts
and lib/use-case-ranking.ts) so that an agent and a reader see the same rows:

- A comparison is the served judgements of a use case that share a comparison group, or one
  judgement that has no group. Its ranked column is its first judgement (stratum order, then ID).
- The metric is the group's headline metric, else the metric most of its results report.
- A configuration's value is the first result on that metric in its last served evaluation there.
  For a comparison with one judgement and no stratum label, the column is also fixed to one
  metric qualifier (none if any result has none, else the first in alphabetical order), and
  evaluations without such a result are skipped.
- Ties share a rank (1, 2, 2, 4). A value in percent is compared as a fraction.
- The use case is ranked on one comparison only: directly relevant before proxy, then the most
  configurations with a value, then one that scores a served baseline, then the comparison ID.
  It needs two configurations with a value and a stated direction.

No composite score is computed: every rank holds for one protocol and one metric.
"""

from __future__ import annotations

import re

BASE = "https://benchmarks.rewire.it/"
ID = BASE + "id/"
RELEASE_GRAPH = f"<{BASE}graph/release>"
DERIVED_GRAPH = f"<{BASE}graph/derived>"
STATUS = BASE + "vocab/status/"
STATE = BASE + "vocab/discrepancy-state/"
RELEVANCE = BASE + "vocab/relevance/"
DIRECTION = BASE + "vocab/direction/"
ORIGIN = BASE + "vocab/origin/"
UNIT = BASE + "vocab/unit/"
MLS_VALUE = "<http://www.w3.org/ns/mls#hasValue>"
SOURCE = "<http://purl.org/dc/terms/source>"
URL = "<https://schema.org/url>"
VERSION = "<https://schema.org/version>"
PARENT = "rb:configurationOf|rb:family|rb:variantOf"
SETTLED = f"<{STATE}explained>, <{STATE}confirmed-error>, <{STATE}false-positive>"


# MIN and MAX are taken over strings, never over IRIs, and turned back with IRI(): rdflib, which
# the tests run on, does not order IRIs in an aggregate; Oxigraph, which the server runs on, does.


def checked(variable: str) -> str:
    """The record is reviewed. Superseded results stay in the graph and are never ranked."""
    return f"{variable} rb:status ?st_{variable[1:]} . FILTER(?st_{variable[1:]} IN (<{STATUS}source_checked>, <{STATUS}reproduced>))"


def served_judgements(s: str = "") -> str:
    """A use case's served judgements with their comparison and their place in it. The stratum
    order and label and the headline metric count only for a judgement with a comparison group."""
    return f"""?j{s} rb:subject $use_case ; rb:relevance ?rel{s} .
      FILTER EXISTS {{ GRAPH {RELEASE_GRAPH} {{ ?j{s} rb:servedEvaluation ?served{s} }} }}
      OPTIONAL {{
        ?j{s} rb:comparisonGroup ?cg{s} .
        OPTIONAL {{ ?j{s} rb:stratumOrder ?ord{s} }}
        OPTIONAL {{ ?j{s} rb:stratumLabel ?lab{s} }}
        OPTIONAL {{ ?j{s} rb:headlineMetric ?hm{s} }}
      }}
      BIND(COALESCE(?cg{s}, STRAFTER(STR(?j{s}), "{ID}")) AS ?g{s})
      BIND(CONCAT(STR(1000000 + COALESCE(?ord{s}, 0)), "|", STR(?j{s})) AS ?key{s})"""


def metric_counts(s: str) -> str:
    """How many reviewed results of a comparison report each metric."""
    return f"""SELECT ?g ?m{s} (COUNT(DISTINCT ?r{s}) AS ?n{s}) WHERE {{
          {served_judgements(s)}
          BIND(?g{s} AS ?g)
          GRAPH {RELEASE_GRAPH} {{ ?j{s} rb:servedEvaluation ?e{s} }}
          ?r{s} rb:evaluation ?e{s} ; rb:metric ?m{s} .
          {checked(f"?r{s}")}
        }} GROUP BY ?g ?m{s}"""


# One row per comparison: its first judgement, layout, relevance and metric.
COMPARISONS = f"""{{ SELECT ?g ?j0 ?strata ?direct ?head WHERE {{
      {{ SELECT ?g (MIN(?key) AS ?firstKey) (MIN(?headKey) AS ?firstHead) (COUNT(DISTINCT ?j) AS ?members)
               (COUNT(?lab) AS ?labels) (MIN(?isDirect) AS ?direct) WHERE {{
        {served_judgements()}
        BIND(IF(?rel = <{RELEVANCE}direct>, 1, 0) AS ?isDirect)
        BIND(COALESCE(IF(isIRI(?hm), ?key, "~"), "~") AS ?headKey)
      }} GROUP BY ?g }}
      BIND(IRI(STRAFTER(?firstKey, "|")) AS ?j0)
      BIND(?members > 1 || ?labels > 0 AS ?strata)
      OPTIONAL {{ ?jh rb:subject $use_case ; rb:headlineMetric ?chosen . FILTER(STR(?jh) = STRAFTER(?firstHead, "|")) }}
      OPTIONAL {{
        {{ SELECT ?g (MIN(STR(?mA)) AS ?common) WHERE {{
          {{ {metric_counts("A")} }}
          {{ SELECT ?g (MAX(?nB) AS ?most) WHERE {{ {{ {metric_counts("B")} }} }} GROUP BY ?g }}
          FILTER(?nA = ?most)
        }} GROUP BY ?g }}
      }}
      BIND(COALESCE(?chosen, IRI(?common)) AS ?head)
    }} }}"""

# For a comparison with one judgement and no stratum label: the qualifier of its ranked column,
# lower-cased. Results without a qualifier count as "", which sorts first.
QUALIFIER = f"""OPTIONAL {{
      {{ SELECT ?j0 ?head (MIN(?lower) AS ?qualifier) WHERE {{
        GRAPH {RELEASE_GRAPH} {{ ?j0 rb:servedEvaluation ?eQ }}
        ?j0 rb:subject $use_case .
        ?rQ rb:evaluation ?eQ ; rb:metric ?head .
        {checked("?rQ")}
        OPTIONAL {{ ?rQ rb:metricQualifier ?qQ }}
        BIND(COALESCE(LCASE(?qQ), "") AS ?lower)
      }} GROUP BY ?j0 ?head }}
    }}"""


# Every reviewed result in a comparison's ranked column: any qualifier for strata, else the
# column's own qualifier. ?ek and ?rk are the evaluation and result IRIs as strings, for ordering.
COLUMN = f"""{{ SELECT ?g ?j0 ?strata ?direct ?head ?c ?ek ?rk WHERE {{
        {COMPARISONS}
        {QUALIFIER}
        ?j0 rb:subject $use_case .
        GRAPH {RELEASE_GRAPH} {{ ?j0 rb:servedEvaluation ?eC }}
        ?eC rb:testedSystem ?c .
        ?c a rb:Configuration .
        ?rC rb:evaluation ?eC ; rb:metric ?head .
        {checked("?rC")}
        OPTIONAL {{ ?rC rb:metricQualifier ?qC }}
        FILTER(?strata || COALESCE(LCASE(?qC), "") = ?qualifier)
        BIND(STR(?eC) AS ?ek) BIND(STR(?rC) AS ?rk)
      }} }}"""

# The ranked column of every comparison: one valued result per configuration. The cell comes
# from the configuration's last served evaluation and, within it, the first result in the column.
# For strata the last evaluation counts whether or not it reports the metric, so a configuration
# whose last evaluation lacks it has no value.
ROWS = f"""{{ SELECT ?g ?direct ?head ?c ?e ?r ?v ?u ?sort ?known WHERE {{
      {{ SELECT ?g ?j0 ?strata ?direct ?head ?c ?lastEk (MIN(?rk) AS ?firstRk) WHERE {{
        {COLUMN}
        {{ SELECT ?j0 ?c (MAX(?ek) AS ?lastEk) WHERE {{
          {COLUMN}
        }} GROUP BY ?j0 ?c }}
        FILTER(?ek = ?lastEk)
      }} GROUP BY ?g ?j0 ?strata ?direct ?head ?c ?lastEk }}
      {{ SELECT ?j0 ?c (MAX(STR(?eA)) AS ?lastServed) WHERE {{
        ?j0 rb:subject $use_case .
        GRAPH {RELEASE_GRAPH} {{ ?j0 rb:servedEvaluation ?eA }}
        ?eA rb:testedSystem ?c .
      }} GROUP BY ?j0 ?c }}
      FILTER(!?strata || ?lastEk = ?lastServed)
      BIND(IRI(?lastEk) AS ?e) BIND(IRI(?firstRk) AS ?r)
      ?r {MLS_VALUE} ?v .
      OPTIONAL {{ ?r rb:unit ?u }}
      OPTIONAL {{ ?r rb:metricDirection ?known . FILTER(?known IN (<{DIRECTION}higher>, <{DIRECTION}lower>)) }}
      BIND(IF(COALESCE(?u = <{UNIT}percent>, false), ?v / 100, ?v) AS ?sort)
    }} }}"""

# The one comparison the use case is ranked on.
CHOSEN = f"""{{ SELECT ?g (IRI(?stated) AS ?dir) WHERE {{
      {{ SELECT ?g ?direct (COUNT(DISTINCT ?c) AS ?valued) (MAX(COALESCE(STR(?known), "")) AS ?stated) (MAX(?isBaseline) AS ?scoresBaseline) WHERE {{
        {ROWS}
        OPTIONAL {{
          GRAPH {RELEASE_GRAPH} {{ $use_case rb:servedBaseline ?b }}
          FILTER(?b = ?c || EXISTS {{ ?c {PARENT} ?b }})
        }}
        BIND(COALESCE(IF(isIRI(?b), 1, 0), 0) AS ?isBaseline)
      }} GROUP BY ?g ?direct }}
      FILTER(?valued >= 2 && STRLEN(?stated) > 0)
    }} ORDER BY DESC(?direct) DESC(?valued) DESC(?scoresBaseline) ?g LIMIT 1 }}"""


def renamed(pattern: str, suffix: str) -> str:
    """The same pattern with every variable renamed, for joining a subquery with a copy of itself.
    rdflib passes outer bindings into a subquery, so the copy must share no variable name."""
    return re.sub(r"\?([A-Za-z_][A-Za-z0-9_]*)", rf"?\g<1>{suffix}", pattern)


def parent(config: str, name: str) -> str:
    """The model, method or pipeline a configuration belongs to. RDF keeps no link order, so a
    configuration with several such links gets the one whose IRI sorts last."""
    return (f"OPTIONAL {{ {{ SELECT {config} (IRI(MAX(STR(?p{name}))) AS ?{name}) WHERE {{ {config} {PARENT} ?p{name} }} "
            f"GROUP BY {config} }} }}")


# The rank is one more than the number of rows in the comparison with a better value. The filter
# on ?rank drops the one empty group rdflib returns when nothing is ranked. Coverage is counted
# per tool over every served comparison of the use case, not only the ranked one.
RANK_FOR_USE_CASE = f"""SELECT ?rank ?configuration ?name ?tool ?value ?unit ?result ?evaluation ?origin ?independent
       ?reviewStatus ?receipt ?evaluated ?relevant
       (GROUP_CONCAT(DISTINCT STR(?finding); separator=" ") AS ?openFindings)
       ?comparison ?protocol ?relevance ?metric ?direction WHERE {{
  {{ SELECT ?g ?direct ?head ?dir ?c ?e ?r ?v ?u (SUM(?better) + 1 AS ?rank) WHERE {{
    {CHOSEN}
    {ROWS}
    {renamed(ROWS, "2")}
    FILTER(?g2 = ?g)
    BIND(IF(IF(?dir = <{DIRECTION}lower>, ?sort2 < ?sort, ?sort2 > ?sort), 1, 0) AS ?better)
  }} GROUP BY ?g ?direct ?head ?dir ?c ?e ?r ?v ?u }}
  FILTER(?rank >= 1)
  ?e rb:testedOn ?protocol .
  ?c rdfs:label ?label .
  OPTIONAL {{ ?c rb:reportedName ?reported }}
  OPTIONAL {{ ?e rb:origin ?origin }}
  {parent("?c", "parent")}
  BIND(COALESCE(?parent, ?c) AS ?tool)
  {{ SELECT ?toolT (COUNT(DISTINCT ?gT) AS ?evaluated) WHERE {{
      {served_judgements("T")}
      GRAPH {RELEASE_GRAPH} {{ ?jT rb:servedEvaluation ?eT }}
      ?eT rb:testedSystem ?cT .
      ?cT a rb:Configuration .
      {parent("?cT", "parentT")}
      BIND(COALESCE(?parentT, ?cT) AS ?toolT)
  }} GROUP BY ?toolT }}
  FILTER(?toolT = ?tool)
  {{ SELECT (COUNT(DISTINCT ?gR) AS ?relevant) WHERE {{
    {served_judgements("R")}
  }} }}
  OPTIONAL {{
    {{ SELECT ?r (IRI(MIN(STR(?receiptSource))) AS ?receipt) WHERE {{
      ?r rb:evaluation ?eS .
      {{ ?r {SOURCE} ?receiptSource }} UNION {{ ?eS {SOURCE} ?receiptSource }}
      GRAPH {RELEASE_GRAPH} {{ ?owner rb:runReceipt ?receiptSource }}
    }} GROUP BY ?r }}
  }}
  OPTIONAL {{
    GRAPH {DERIVED_GRAPH} {{
      {{ ?finding rb:outlierResult ?r }} UNION {{ ?finding rb:consensusResult ?r }} UNION {{ ?finding rb:partyResult ?r }}
      ?finding rb:reviewState ?state .
      FILTER(?state NOT IN ({SETTLED}))
    }}
  }}
  BIND(?c AS ?configuration) BIND(?r AS ?result) BIND(?e AS ?evaluation) BIND(?v AS ?value) BIND(?u AS ?unit)
  BIND(COALESCE(?reported, ?label) AS ?name)
  BIND(COALESCE(?origin = <{ORIGIN}independent_paper>, false) AS ?independent)
  BIND(COALESCE(IF(isIRI(?receipt), "reproduced", "source_checked"), "source_checked") AS ?reviewStatus)
  BIND(?g AS ?comparison) BIND(?head AS ?metric) BIND(?dir AS ?direction)
  BIND(IF(?direct = 1, <{RELEVANCE}direct>, <{RELEVANCE}proxy>) AS ?relevance)
}} GROUP BY ?rank ?configuration ?name ?tool ?value ?unit ?result ?evaluation ?origin ?independent
       ?reviewStatus ?receipt ?evaluated ?relevant ?comparison ?protocol ?relevance ?metric ?direction
ORDER BY ?rank LCASE(?name) ?configuration"""


def study(source: str, s: str) -> str:
    """One key per study: the source's DOI, else the DOI or IRI of the paper it is a companion of
    (a repository, supplement or other version), else the source itself."""
    return f"""OPTIONAL {{ {source} rb:doi ?doi{s} }}
          OPTIONAL {{ {source} rb:companionOf ?paper{s} . OPTIONAL {{ ?paper{s} rb:doi ?paperDoi{s} }} }}
          BIND(COALESCE(LCASE(STR(?doi{s})), LCASE(STR(?paperDoi{s})), STR(?paper{s}), STR({source})) AS ?study{s})"""


def evidence(s: str, protocol: str = "") -> str:
    """Served evidence of a use case: its evaluations, whether a judgement is directly relevant,
    whether an evaluation is independent, and the studies the reviewed results cite."""
    return f"""?j{s} rb:subject ?useCase ; rb:relevance ?rel{s} .
          FILTER(COALESCE(?useCase = $use_case, true))
          GRAPH {RELEASE_GRAPH} {{ ?j{s} rb:servedEvaluation ?e{s} }}
          {protocol}
          OPTIONAL {{ ?e{s} rb:origin ?origin{s} }}
          OPTIONAL {{
            ?r{s} rb:evaluation ?e{s} ; {SOURCE} ?src{s} .
            {checked(f"?r{s}")}
            {study(f"?src{s}", s)}
          }}
          BIND(IF(?rel{s} = <{RELEVANCE}direct>, 1, 0) AS ?isDirect{s})
          BIND(IF(COALESCE(?origin{s} = <{ORIGIN}independent_paper>, false), 1, 0) AS ?isIndependent{s})"""


# A use case with no depth tier counts as tier -1, so that a given tier does not match it: an
# unbound ?depthTier would make the comparison an error, which COALESCE turns into true.
# Use-case rows come first: they are few, and protocol rows are mostly single_source.
GAPS = f"""SELECT ?useCase ?useCaseName ?depthTier ?level ?protocol ?protocolName ?gap ?evaluations ?studies WHERE {{
  ?useCase a rb:UseCase ; rdfs:label ?useCaseName .
  OPTIONAL {{ ?useCase rb:depthTier ?depthTier }}
  FILTER(COALESCE(?useCase = $use_case, true))
  FILTER(COALESCE(COALESCE(?depthTier, -1) = $tier, true))
  {{
    ?useCase a rb:UseCase .
    OPTIONAL {{
      {{ SELECT ?useCase (COUNT(DISTINCT ?eU) AS ?servedU) (COUNT(DISTINCT ?studyU) AS ?studiesU)
               (MAX(?isIndependentU) AS ?independentU) (MAX(?isDirectU) AS ?directU) WHERE {{
          {evidence("U")}
      }} GROUP BY ?useCase }}
    }}
    BIND(COALESCE(?servedU, 0) AS ?evaluations) BIND(COALESCE(?studiesU, 0) AS ?studies)
    BIND("use_case" AS ?level)
    VALUES ?gap {{ "no_direct_evidence" "single_source" "no_independent_result" }}
    FILTER((?gap = "no_direct_evidence" && COALESCE(?directU, 0) = 0)
        || (?gap = "single_source" && ?studies = 1)
        || (?gap = "no_independent_result" && ?evaluations > 0 && ?independentU = 0))
  }} UNION {{
    ?useCase rb:assessedBy ?protocol .
    ?protocol rdfs:label ?protocolName .
    OPTIONAL {{
      {{ SELECT ?useCase ?protocol (COUNT(DISTINCT ?eP) AS ?servedP) (COUNT(DISTINCT ?studyP) AS ?studiesP)
               (MAX(?isIndependentP) AS ?independentP) WHERE {{
          {evidence("P", "?eP rb:testedOn ?protocol .")}
      }} GROUP BY ?useCase ?protocol }}
    }}
    BIND(COALESCE(?servedP, 0) AS ?evaluations) BIND(COALESCE(?studiesP, 0) AS ?studies)
    BIND("protocol" AS ?level)
    VALUES ?gap {{ "no_served_evidence" "single_source" "no_independent_result" }}
    FILTER((?gap = "no_served_evidence" && ?evaluations = 0)
        || (?gap = "single_source" && ?studies = 1)
        || (?gap = "no_independent_result" && ?evaluations > 0 && ?independentP = 0))
  }}
  FILTER(COALESCE(?level = $level, true))
}} ORDER BY DESC(?level) ?useCase ?protocol ?gap"""

RECIPE_FOR = f"""SELECT ?record ?recordName ?storeRecipes ?fullProtocolReceipt ?receiptName ?receiptUrl ?receiptRevision ?receiptDate WHERE {{
  {{ ?record rb:runRecipes ?storeRecipes . FILTER(?record = $subject) }}
  UNION {{ ?record rb:within $subject ; rb:runRecipes ?storeRecipes }}
  UNION {{ $subject rb:within ?record . ?record rb:runRecipes ?storeRecipes }}
  ?record rdfs:label ?recordName .
  OPTIONAL {{
    GRAPH {RELEASE_GRAPH} {{ ?record rb:runReceipt ?fullProtocolReceipt }}
    ?fullProtocolReceipt rdfs:label ?receiptName .
    OPTIONAL {{ ?fullProtocolReceipt {URL} ?receiptUrl }}
    OPTIONAL {{ ?fullProtocolReceipt {VERSION} ?receiptRevision }}
    OPTIONAL {{ ?fullProtocolReceipt rb:retrievedAt ?receiptDate }}
  }}
}} ORDER BY ?record ?fullProtocolReceipt"""

# Only a result has provenance here: another record's IRI returns nothing. The isIRI filter drops
# the one empty group rdflib returns when the review subquery matches nothing.
PROVENANCE = f"""SELECT ?step ?record ?name ?locator ?url ?doi ?retrieved ?sha256 ?status ?reviewedBy ?reviewMethod ?date ?field ?value WHERE {{
  {{
    $result a rb:Result ; {SOURCE} ?record ; rb:sourceLocator ?locator .
    ?record rdfs:label ?name ; rb:status ?status .
    OPTIONAL {{ ?record {URL} ?url }}
    OPTIONAL {{ ?record rb:doi ?doi }}
    OPTIONAL {{ ?record rb:retrievedAt ?retrieved }}
    OPTIONAL {{ ?record rb:artifactSha256 ?sha256 }}
    BIND("source" AS ?step)
  }} UNION {{
    {{ SELECT ?record ?name ?status ?date (GROUP_CONCAT(DISTINCT STR(?by); separator=" ") AS ?reviewedBy)
             (GROUP_CONCAT(DISTINCT STR(?method); separator=" ") AS ?reviewMethod) WHERE {{
      $result a rb:Result .
      {{ BIND($result AS ?record) }} UNION {{ $result rb:evaluation ?record }}
      ?record rdfs:label ?name ; rb:status ?status .
      OPTIONAL {{ ?record rb:reviewedBy ?by }}
      OPTIONAL {{ ?record rb:reviewMethod ?method }}
      OPTIONAL {{ ?record rb:reviewDate ?reviewDate }}
      OPTIONAL {{ ?record rb:reviewedAt ?reviewedAt }}
      BIND(COALESCE(STR(?reviewDate), STR(?reviewedAt)) AS ?date)
    }} GROUP BY ?record ?name ?status ?date }}
    FILTER(isIRI(?record))
    BIND("review" AS ?step)
  }} UNION {{
    $result a rb:Result .
    ?record rb:subject $result ; rdfs:label ?name ; rb:status ?status ; rb:claimField ?field .
    OPTIONAL {{ ?record rb:value ?value }}
    OPTIONAL {{ ?record rb:sourceLocator ?locator }}
    OPTIONAL {{ ?record rb:reviewDate ?reviewDate }}
    OPTIONAL {{ ?record rb:date ?actionDate }}
    BIND(COALESCE(STR(?actionDate), STR(?reviewDate)) AS ?date)
    BIND("claim" AS ?step)
  }}
}} ORDER BY DESC(?step) ?date ?record"""


# Bundle format: rdf-kg-mcp docs/bundle-format.md, "Named queries". No parameter is used in a
# SELECT list or in BOUND(); an optional one appears only as FILTER(COALESCE(?x = $p, true)).
QUERIES = [
    {
        "name": "rank_for_use_case",
        "title": "Ranked configurations for a use case, on its one comparable protocol",
        "description": "The rows of the use case's board on the website: configurations ranked on one "
        "comparison, one column and one metric, best first, ties sharing a rank. A directly relevant "
        "comparison is used when one qualifies, else a proxy one (see relevance). Each row has the result and "
        "evaluation it is read from, the tool it belongs to, who produced the result (origin; independent is "
        "true only for an independent study, so a Rewire run is not independent), the review status "
        "(reproduced only when the result or its evaluation cites an executed full-protocol run receipt, "
        "given in receipt), coverage (evaluated: how many of the use case's served comparisons score the "
        "tool; relevant: how many there are) and the unsettled discrepancies the ranked result takes part in "
        "(openFindings, IRIs separated by spaces). No composite score: a rank holds for this protocol only. "
        "No rows means the release ranks nothing for the use case, or that use_case is not a use case record. "
        "A record ID is not always use-case- followed by the website slug: find the record by its slug, "
        '?useCase rb:slug "protein-variant-stability".',
        "sparql": RANK_FOR_USE_CASE,
        "params": [
            {"name": "use_case", "type": "iri", "required": True,
             "description": "The use case record, e.g. id:use-case-splicing-follow-up. Look it up by rb:slug; "
             "do not build it from the website slug."},
        ],
    },
    {
        "name": "gaps",
        "title": "Evidence gaps for use cases and their protocols",
        "description": "Where the served evidence is thin. For a use case (level use_case): "
        "no_direct_evidence (no served judgement is directly relevant), single_source (every served result "
        "comes from one study) and no_independent_result (no served evaluation is from an independent "
        "study). For each protocol a use case is assessed by (level protocol): no_served_evidence (the "
        "release serves no evaluation on it for this use case), single_source and no_independent_result. "
        "evaluations and studies are the counts behind the row. A study is a DOI, or a source and the "
        "paper it is a companion of. Use-case rows come first. With no parameter the result is several "
        "hundred rows, most of them protocols with one study: set level to use_case for the short list.",
        "sparql": GAPS,
        "params": [
            {"name": "use_case", "type": "iri", "required": False,
             "description": "Only this use case, e.g. id:use-case-splicing-follow-up (look it up by rb:slug). "
             "Leave unset for all."},
            {"name": "tier", "type": "integer", "required": False,
             "description": "Only use cases of this depth tier: 1, 2 or 3 (docs/tiers.md). Leave unset for all."},
            {"name": "level", "type": "string", "required": False,
             "description": "Only rows of this level: use_case or protocol. Leave unset for both."},
        ],
    },
    {
        "name": "recipe_for",
        "title": "Run recipes and run receipts recorded for a benchmark, protocol or model",
        "description": "Records that carry run recipes: the given record, the protocols and tasks inside it, "
        "and the benchmarks it is inside. storeRecipes is the record's recipes as stored (JSON: each has an "
        "id and instructions with a status of source_reviewed_not_executed, smoke_tested or executed). "
        "fullProtocolReceipt is the source record of a run receipt on an executed full-protocol instruction, "
        "with its URL, revision and date. The store does not yet record a pointer to a recipe file in "
        "rewire-benchmarks or a status for one: a recipe file there names its store recipe in "
        "store_recipe_id and its record in kg_record_id. A receipt here is evidence for the stored "
        "instruction it is attached to, not for a recipe file written later.",
        "sparql": RECIPE_FOR,
        "params": [
            {"name": "subject", "type": "iri", "required": True,
             "description": "A benchmark, protocol, task or model record, e.g. id:rewire-mfass-v2."},
        ],
    },
    {
        "name": "provenance",
        "title": "Sources, locator, capture and review history of one result",
        "description": "Where a result comes from and who checked it. step source: each source the result "
        "cites, with the locator of the value in it, its URL and DOI, when its artifact was retrieved and the "
        "artifact's SHA-256. step review: the review of the result and of its evaluation (status, reviewers, "
        "methods and date). step claim: each claim about the result, such as a correction or a discrepancy "
        "review, with the field it is about and its date. No rows means result is not a result record.",
        "sparql": PROVENANCE,
        "params": [
            {"name": "result", "type": "iri", "required": True,
             "description": "The result record, e.g. id:rewire-result-pangolin-maskfalse-auroc."},
        ],
    },
]
