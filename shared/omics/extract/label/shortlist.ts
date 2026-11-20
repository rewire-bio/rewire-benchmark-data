/** The deterministic pre-filter: which stored records a table could plausibly be about.
 *
 * The store holds 2,242 records of a kind that can carry results. Putting all of them in front
 * of the stage would be expensive and would make the answer unverifiable: a shortlist of
 * everything is not a shortlist. Putting one in front of it would be deciding the question
 * here, with no evidence, which is what the deterministic pass already declined to do.
 *
 * So the filter is two rules, both written down, both reported separately, because they bound
 * different things.
 *
 *   cites_this_source   the record already names this source in `source_ids`, or names a
 *                       source the store joins to it with `companion_of`. This is the store
 *                       saying the two are connected, and it is strong. It is also circular
 *                       for the job of extracting results nobody has extracted yet: a source
 *                       nothing cites gets nothing from this rule, which is why the
 *                       measurement reports the other rule on its own.
 *   name_in_table       the content words of the record's printed name occur in the words the
 *                       table prints: its caption or label, and its column headings. This is
 *                       the rule that has to carry a source the store has never seen.
 *
 * Neither rule decides anything. They narrow, and the narrowing is what the measurement is
 * about: a shortlist that does not hold the right answer bounds everything the stage can
 * achieve, whatever it then does.
 *
 * No fuzzy matching, no stemming, no edit distance. `shared/omics/extract/labels.ts` records
 * why for the exact-match lookups, and the same reasoning holds one step weaker here: a
 * shortlist built by a rule nobody can restate is a shortlist nobody can check. The cost is
 * that a record named in words the table does not print is missed, and that cost is measured
 * rather than hidden.
 */
import { normaliseLabel } from "../../spans/table";
import { assessmentKinds as kinds } from "../decide";

/** Record kinds a table caption may be naming. Taken from `shared/omics/extract/decide.ts`,
 * which is the list the deterministic pass matches against, so the two stages narrow over the
 * same kinds. */
export { assessmentKinds } from "../decide";

/** The fields of a stored record this filter reads. Structural, so the caller passes whatever
 * `readKind` returns without a conversion. */
export interface AssessmentRecord {
  id: string;
  kind: string;
  name?: string;
  source_ids?: string[];
  links?: { relation: string; target_id: string }[];
  attributes?: Record<string, unknown>;
}

/** The source records the filter reads, for the `companion_of` edges only. */
export interface SourceRecord {
  id: string;
  links?: { relation: string; target_id: string }[];
}

/**
 * Words that say nothing about which benchmark a table reports.
 *
 * Grammatical words only, plus the three words a table caption prints about itself. Every word
 * added here loosens the filter by letting a record match on less, so the list is closed, it
 * is short, and a change to it changes the measured shortlist sizes and has to be re-measured.
 * Words that look generic but carry meaning in this store, "benchmark", "task", "prediction",
 * "accuracy", are deliberately absent: they are most of what a benchmark is called.
 */
export const STOP_WORDS = new Set([
  "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with",
  "table", "figure", "supplementary",
]);

/** How many records a shortlist may hold.
 *
 * Fifteen over 2,242 is a narrowing of two orders of magnitude and still a list a reader can
 * check by eye in a receipt. The cap binds after both rules, so a source with more than
 * fifteen records citing it loses the lowest-scoring of them, which the entry count reports. */
export const SHORTLIST_MAX = 15;

/** The share of a record's content words that must occur in the table's words.
 *
 * Half, which admits "Plant Genomic Benchmark" against a caption printing "plant genomic", and
 * refuses a four-word name on one shared word. It is a threshold on a ratio rather than a
 * count so that a long name is not easier to match than a short one. */
export const NAME_WORD_SHARE = 0.5;

export interface ShortlistEntry {
  id: string;
  kind: string;
  name: string;
  /** Which rules put it here. Both is the strongest and is the common case for a source the
   * store already holds records for. */
  why: ("cites_this_source" | "name_in_table")[];
  /** The share of the record's content words the table prints, 0 where the lexical rule did
   * not admit it. */
  name_word_share: number;
}

export interface Shortlist {
  /** The ids, sorted, which is the order the question prints them in. Sorted rather than
   * ranked so that the order carries no hint about which one the filter prefers. */
  ids: string[];
  entries: ShortlistEntry[];
  /** How many records of a result-carrying kind the store holds, so a reader can see the
   * narrowing rather than take it on trust. */
  considered: number;
  /** Entries the cap held back, counted. */
  held_back: number;
}

/** Every lookup the filter needs, built once per run. */
export interface ShortlistIndex {
  records: Map<string, AssessmentRecord>;
  /** The printed names of a record: its `name` and its `reported_name`, normalised. */
  namesOf: Map<string, string[]>;
  /** The content words of each record's printed names, one set per record. */
  wordsOf: Map<string, Set<string>>;
  /** Source id to the assessment records citing it. */
  bySource: Map<string, string[]>;
  /** Source id to the sources the store joins it to with `companion_of`, both ways. */
  companions: Map<string, string[]>;
  considered: number;
}

/** The content words of a printed string: normalised, split on anything that is not a letter
 * or a digit, with the stop words and the single characters dropped.
 *
 * Splitting on punctuation is what makes "SupTable8_Tool_performance" four words and
 * "CASF-2016" two. A single character is dropped because a table that prints "A" and a record
 * named "A" are not evidence of each other. */
export function contentWords(text: string): string[] {
  return normaliseLabel(text)
    .split(/[^\p{L}\p{N}]+/u)
    .filter((word) => word.length > 1 && !STOP_WORDS.has(word));
}

const push = (index: Map<string, string[]>, key: string, value: string) => {
  const held = index.get(key);
  if (held) { if (!held.includes(value)) held.push(value); }
  else index.set(key, [value]);
};

/**
 * Build the lookups from the store's own records.
 *
 * `records` are the records of a kind that can carry results. `sources` are the source records,
 * read only for their `companion_of` edges: a supplementary workbook and the paper it belongs
 * to are one study, and a benchmark cited on one of them is evidence for a table in the other.
 */
export function buildShortlistIndex(records: AssessmentRecord[], sources: SourceRecord[] = []): ShortlistIndex {
  // Filtered here rather than left to the caller. A model or a dataset on a shortlist is a
  // record the stage could pick and `check.ts` would then refuse, which is a question asked
  // and paid for to produce a refusal that was knowable before it was asked.
  const carriers = records.filter((record) => (kinds as readonly string[]).includes(record.kind));
  const index: ShortlistIndex = {
    records: new Map(),
    namesOf: new Map(),
    wordsOf: new Map(),
    bySource: new Map(),
    companions: new Map(),
    considered: carriers.length,
  };
  for (const record of carriers) {
    index.records.set(record.id, record);
    const printed: string[] = [];
    if (record.name) printed.push(record.name);
    const reported = record.attributes?.reported_name;
    if (typeof reported === "string") printed.push(reported);
    index.namesOf.set(record.id, printed.map(normaliseLabel).filter((name) => name !== ""));
    index.wordsOf.set(record.id, new Set(printed.flatMap(contentWords)));
    for (const source of record.source_ids ?? []) push(index.bySource, source, record.id);
  }
  for (const source of sources)
    for (const link of source.links ?? []) {
      if (link.relation !== "companion_of") continue;
      push(index.companions, source.id, link.target_id);
      push(index.companions, link.target_id, source.id);
    }
  return index;
}

/** The words a table prints that the filter reads: its caption or label, and its column
 * headings. Row labels are left out on purpose. A row names what was evaluated, which is the
 * `model` field and a different question; letting a row label pull a benchmark into the
 * shortlist would put the wrong kind of record in front of the stage. */
export function tableWords(table: { anchor_text: string; column_headers: string[] }): Set<string> {
  return new Set([table.anchor_text, ...table.column_headers].flatMap(contentWords));
}

/**
 * The shortlist for one table.
 *
 * Deterministic in both rules and in the order, so the same table and the same store give the
 * same bytes, which is what lets the cache key stand for the question that was asked.
 */
export function shortlistFor(
  index: ShortlistIndex,
  table: { source_id: string; anchor_text: string; column_headers: string[] },
): Shortlist {
  const words = tableWords(table);
  const cites = new Set<string>();
  const sources = [table.source_id, ...(index.companions.get(table.source_id) ?? [])];
  for (const source of sources) for (const id of index.bySource.get(source) ?? []) cites.add(id);

  const scored = new Map<string, number>();
  for (const [id, recordWords] of index.wordsOf) {
    if (recordWords.size === 0) continue;
    let hits = 0;
    for (const word of recordWords) if (words.has(word)) hits += 1;
    const share = hits / recordWords.size;
    if (share >= NAME_WORD_SHARE) scored.set(id, share);
  }

  const all = [...new Set([...cites, ...scored.keys()])].map((id) => {
    const record = index.records.get(id);
    const why: ShortlistEntry["why"] = [];
    if (cites.has(id)) why.push("cites_this_source");
    if (scored.has(id)) why.push("name_in_table");
    return {
      id,
      kind: record?.kind ?? "",
      name: record?.name ?? "",
      why,
      name_word_share: scored.get(id) ?? 0,
    };
  });

  // Rank for the cap only: the store's own citation first, then the share of the name the
  // table prints, then the id so that two equal entries never swap between runs.
  const ranked = [...all].sort((a, b) => {
    const cited = Number(b.why.includes("cites_this_source")) - Number(a.why.includes("cites_this_source"));
    if (cited !== 0) return cited;
    if (b.name_word_share !== a.name_word_share) return b.name_word_share - a.name_word_share;
    return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
  });
  const kept = ranked.slice(0, SHORTLIST_MAX).sort((a, b) => (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));

  return {
    ids: kept.map((entry) => entry.id),
    entries: kept,
    considered: index.considered,
    held_back: Math.max(0, ranked.length - kept.length),
  };
}
