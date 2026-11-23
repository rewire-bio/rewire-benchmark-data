/** A ranked keyword search over record names, aliases and descriptions.
 *
 * This is the second way to build a shortlist, behind a flag, and it exists to be measured
 * against the exact word rule in `shortlist.ts`. It is not the default and nothing uses it
 * unless a caller asks for it by name.
 *
 * The scoring is a port of the text score in `rdf-kg-mcp`'s `search.py`, which is what the
 * knowledge graph's `search` tool ranks with: each query word is matched against the words of
 * each field after light suffix stripping, exactly or as a prefix of a longer word; a field
 * match is weighted (name 3, alias 2, description 1) and normalised by the field's length, so
 * a short name that matches beats a long sentence that mentions the word; names and aliases
 * are also indexed squashed, so "ESM2" finds "ESM-2". The constants are the same.
 *
 * Two parts of that tool are left out on purpose, so a number measured here is not that tool's
 * number. Its class rarity prior multiplies a score by how rare the record's class is, which
 * over these three kinds would lift a benchmark about tenfold over a protocol, and nearly every
 * right answer in the held-out set is a protocol. Its diversification lets one class take at
 * most three of the leading places, which reshapes a list of ten. Both serve a search over
 * every class in the graph and neither serves a shortlist over three.
 *
 * It runs in this process over the records the caller already read. It opens no socket and
 * reads no bundle.
 */

/** The fields a record is searched in, and what a match in each is worth. */
export const SEARCH_FIELD_WEIGHTS = { name: 3, alias: 2, description: 1 } as const;
export type SearchField = keyof typeof SEARCH_FIELD_WEIGHTS;

/** What a prefix match is worth against an exact one, and the shortest stem that may match
 * as a prefix. */
export const PREFIX_WEIGHT = 0.6;
export const MIN_PREFIX = 4;
/** The BM25 constants. */
export const K1 = 1.2;
export const B = 0.75;

const SUFFIXES = ["ing", "ed", "es", "e", "s"];
/** Squashed terms share the postings with word stems, behind a prefix no word can start with. */
const SQUASH_MARK = "\u0000";
const SQUASHED: Partial<Record<SearchField, string>> = { name: "name_squashed", alias: "alias_squashed" };
const UNSQUASHED: Record<string, SearchField> = { name_squashed: "name", alias_squashed: "alias" };

/** Strip one common English suffix, keeping at least four characters. */
export function stem(word: string): string {
  for (const suffix of SUFFIXES)
    if (word.length - suffix.length >= 4 && word.endsWith(suffix)) return word.slice(0, -suffix.length);
  return word;
}

const runs = (text: string): string[] => text.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? [];

/** The stems of the words a string prints: runs of letters and digits, lower case. */
export const searchWords = (text: string): string[] => runs(text).map(stem);

/** Letters and digits only, lower case: "ESM-2" and "esm 2" both give "esm2". */
export const squash = (text: string): string => runs(text).join("");

/** The whole query squashed, then each chunk between spaces, without repeats. */
const squashedTerms = (text: string): string[] =>
  [...new Set([text, ...text.split(/\s+/)].map(squash))].filter((term) => term !== "").map((term) => SQUASH_MARK + term);

/** The text of one record, by field. */
export interface SearchDocument {
  id: string;
  name?: string;
  aliases?: string[];
  description?: string;
}

export interface SearchIndex {
  /** Term to record id to how many times each field prints it. */
  postings: Map<string, Map<string, Record<string, number>>>;
  /** Record id to the length of each of its fields, in terms. */
  lengths: Map<string, Record<string, number>>;
  /** The mean length of each field, over the records that have it. */
  average: Record<string, number>;
  /** Every term, sorted, for the prefix lookup. */
  terms: string[];
}

/** Index the documents once. */
export function buildSearchIndex(documents: SearchDocument[]): SearchIndex {
  const postings: SearchIndex["postings"] = new Map();
  const lengths: SearchIndex["lengths"] = new Map();
  const add = (id: string, field: string, tokens: string[]) => {
    if (tokens.length === 0) return;
    const held = lengths.get(id) ?? {};
    held[field] = (held[field] ?? 0) + tokens.length;
    lengths.set(id, held);
    for (const token of tokens) {
      const posting = postings.get(token) ?? new Map<string, Record<string, number>>();
      const counts = posting.get(id) ?? {};
      counts[field] = (counts[field] ?? 0) + 1;
      posting.set(id, counts);
      postings.set(token, posting);
    }
  };
  for (const document of documents) {
    const fields: [SearchField, string[]][] = [
      ["name", document.name ? [document.name] : []],
      ["alias", document.aliases ?? []],
      ["description", document.description ? [document.description] : []],
    ];
    for (const [field, values] of fields)
      for (const value of values) {
        const tokens = searchWords(value);
        if (tokens.length === 0) continue;
        add(document.id, field, tokens);
        const squashed = SQUASHED[field];
        if (squashed) add(document.id, squashed, [SQUASH_MARK + squash(value)]);
      }
  }
  const totals: Record<string, number> = {};
  const counts: Record<string, number> = {};
  for (const held of lengths.values())
    for (const [field, length] of Object.entries(held)) {
      totals[field] = (totals[field] ?? 0) + length;
      counts[field] = (counts[field] ?? 0) + 1;
    }
  const average: Record<string, number> = {};
  for (const field of Object.keys(totals)) average[field] = totals[field] / counts[field];
  return { postings, lengths, average, terms: [...postings.keys()].sort() };
}

/** The indexed terms a query term matches: itself, and every longer word it is a prefix of. */
function expand(index: SearchIndex, term: string): [string, number][] {
  const matches: [string, number][] = index.postings.has(term) ? [[term, 1]] : [];
  // A squashed term matches whole only. A prefix of a squashed name is not a word boundary.
  if (term.length < MIN_PREFIX || term.startsWith(SQUASH_MARK)) return matches;
  let low = 0;
  let high = index.terms.length;
  while (low < high) {
    const middle = (low + high) >> 1;
    if (index.terms[middle] <= term) low = middle + 1;
    else high = middle;
  }
  for (let at = low; at < index.terms.length && index.terms[at].startsWith(term); at += 1)
    matches.push([index.terms[at], PREFIX_WEIGHT]);
  return matches;
}

/** The score of every record that matches any word of the query. */
export function searchScores(index: SearchIndex, query: string): Map<string, number> {
  const scores = new Map<string, number>();
  const documents = Math.max(1, index.lengths.size);
  for (const queryTerm of new Set([...searchWords(query), ...squashedTerms(query)]))
    for (const [term, weight] of expand(index, queryTerm)) {
      const posting = index.postings.get(term)!;
      const idf = Math.log(1 + (documents - posting.size + 0.5) / (posting.size + 0.5));
      for (const [id, fields] of posting) {
        const lengths = index.lengths.get(id)!;
        let total = 0;
        for (const [field, count] of Object.entries(fields)) {
          const norm = 1 - B + (B * lengths[field]) / index.average[field];
          total += (SEARCH_FIELD_WEIGHTS[UNSQUASHED[field] ?? (field as SearchField)] * count * (K1 + 1)) / (count + K1 * norm);
        }
        scores.set(id, (scores.get(id) ?? 0) + weight * idf * total);
      }
    }
  return scores;
}

/** The matching records, best first. Equal scores fall back to the id, so two runs agree. */
export function searchRanked(index: SearchIndex, query: string): { id: string; score: number }[] {
  return [...searchScores(index, query)]
    .map(([id, score]) => ({ id, score }))
    .sort((a, b) => (b.score !== a.score ? b.score - a.score : a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}
