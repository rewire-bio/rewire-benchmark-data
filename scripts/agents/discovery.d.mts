export const DEFAULT_REPO: string;
export const ARTICLE_REPO: string;
export const PROMPT_PATH: string;
export const FIXTURES: string;
export const MODELS: { scan: string; judge: string; triage: string };
export const LIMITS: Record<string, number>;
export const PRICES: Record<string, any>;
export const AREAS: string[];
export const GENOMIC_AREAS: string[];
export const PROTEIN_AREAS: string[];
export const KINDS: string[];
export const SCAN_LANES: { name: string; focus: string }[];
export const LABELS: Record<string, { color: string; description: string }>;
export const JUDGEMENT_SCHEMA: Record<string, any>;
export type Tier = 1 | 2 | 3;
export interface Issue { repo: string; number: number; title: string; body?: string | null; html_url?: string; state?: string; labels?: string[]; created_at?: string; user?: string }
export interface Article { url: string; title: string }
export type Candidate = Record<string, any>;
export function tierOf(areas?: string[]): Tier;
export function dataLabels(tier: Tier): string[];
export function normalise(text: unknown): string;
export function keyOf(name: string): string;
export function matchForm(text: unknown): string;
export function spellForm(text: unknown): string;
export interface Rejected { name: string; names: string[]; date: string; reason: string }
export function nearMatches(candidate: Candidate, known: { issues?: Issue[]; storeNames?: Map<string, string> }, limit?: number): string[];
export function verdictOf(notes: unknown): "FILE" | "SKIP" | null;
export function readRejected(path: string, notes?: string[]): Rejected[];
export function findRejected(candidate: Candidate, rejected: Rejected[], runDate: string, days: number): { where: string; ref: string; reason: string } | null;
export function markersIn(body: string | null | undefined): string[];
export function identifiersOf(candidate: Candidate): string[];
export function findDuplicate(candidate: Candidate, known: { issues?: Issue[]; storeNames?: Map<string, string>; articles?: Article[] }): { where: string; ref: string; url?: string; reason: string } | null;
export function findArticle(candidate: Candidate, articles?: Article[]): Article | null;
export function readStoreNames(dir?: string, form?: (text: unknown) => string): Promise<Map<string, string>>;
export function clean(text: unknown): string;
export function renderDataIssue(candidate: Candidate, opts: { tier: Tier; runDate: string; article?: { url?: string; inline?: boolean } | null; existingArticle?: Article | null; dedupNote: string }): { title: string; body: string; labels: string[] };
export function renderArticleIssue(candidate: Candidate, opts: { dataUrl: string; runDate: string; dedupNote: string }): { title: string; body: string; labels: string[] };
export function planFiling(candidates: Candidate[], opts: { issues: Issue[]; storeNames: Map<string, string>; articles: Article[]; articleAccess: boolean; runDate: string; maxPairs?: number; filedToday?: number }): { file: { candidate: Candidate; tier: Tier; existingArticle: Article | null; dedupNote: string }[]; skipped: { name: string; reason: string }[] };
export function ageInDays(released: unknown, runDate: string): number | null;
export function knownTitles(issues: Issue[], repo: string, limit?: number): string[];
export function scanPrompt(input: { lane: { name: string; focus: string }; runDate: string; lookbackDays: number; titles: string[]; rejected?: string[] }): string;
export class Usage {
  byModel: Record<string, { input: number; output: number; cacheWrite: number; cacheRead: number; webSearches: number; webFetches: number }>;
  calls: number;
  add(model: string, usage: any, assumed?: { web_search_requests?: number; web_fetch_requests?: number }): void;
  costOf(model: string): number;
  total(): number;
  table(): string;
}
export interface LaneDrop { name: string; category: "known" | "remembered" | "other"; reason: string }
export interface LaneReport { lane: string; focus?: string; status: string; requests: Record<string, any>[]; activity?: Record<string, any>[]; notes?: string; raw_candidates: Candidate[] | null; dropped: LaneDrop[]; to_judge: string[] }
export function toolActivity(content: unknown, cap?: number): Record<string, any>[];
export function queriesOf(activity: Record<string, any>[]): string[];
export function callCounts(activity: Record<string, any>[] | undefined): { direct_searches: number; code_searches: number; direct_fetches: number; code_fetches: number };
export const DIRECT_ONLY: string[];
export function triageLane(candidates: Candidate[], opts: { isKnown: (candidate: Candidate) => { where: string; reason: string } | null; seen: Map<string, string> }): { fresh: Candidate[]; dropped: LaneDrop[] };
export function laneReport(lane: { name: string; focus?: string }): LaneReport;
export function laneCounts(report: LaneReport): { searches: number; fetches: number; direct_searches: number; code_searches: number; direct_fetches: number; code_fetches: number; output_tokens: number; raw: number; known: number; remembered: number; other: number; to_judge: number };
export function scanEnding(requests: Record<string, any>[]): string;
export function laneLine(report: LaneReport): string;
export function redactor(env?: Record<string, string | undefined>): (text: unknown) => string;
export function writeLaneReports(out: string, reports: LaneReport[], opts: { mode: string; runDate: string; redact?: (text: unknown) => string }): void;
export function renderSummary(input: { mode: string; runDate: string; usage: Usage; filed: any[]; skipped: { name: string; reason: string }[]; notes?: string[]; lanes?: LaneReport[] }): string;
export function githubClient(token: string, fetchImpl?: typeof fetch): any;
export function parseBlogIndex(html: string, base?: string): Article[];
export interface Planned { name: string; tier: Tier; labels: string[]; title: string; data: { title: string; body: string; labels: string[] }; article: { title: string; body: string; labels: string[] } | null; dataUrl?: string; articleUrl?: string; articleNote?: string }
export function main(argv?: string[], env?: Record<string, string | undefined>, deps?: Record<string, any>): Promise<{ summary: string; planned: Planned[]; skipped?: { name: string; reason: string }[]; usage?: Usage; lanes?: LaneReport[] }>;
