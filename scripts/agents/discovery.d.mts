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
export const LABELS: Record<string, { color: string; description: string }>;
export const JUDGEMENT_SCHEMA: Record<string, any>;
export type Tier = 1 | 2 | 3;
export interface Issue { repo: string; number: number; title: string; body?: string | null; html_url?: string; state?: string }
export interface Article { url: string; title: string }
export type Candidate = Record<string, any>;
export function tierOf(areas?: string[]): Tier;
export function dataLabels(tier: Tier): string[];
export function normalise(text: unknown): string;
export function keyOf(name: string): string;
export function markersIn(body: string | null | undefined): string[];
export function identifiersOf(candidate: Candidate): string[];
export function findDuplicate(candidate: Candidate, known: { issues?: Issue[]; storeNames?: Map<string, string>; articles?: Article[] }): { where: string; ref: string; url?: string; reason: string } | null;
export function findArticle(candidate: Candidate, articles?: Article[]): Article | null;
export function readStoreNames(dir?: string): Promise<Map<string, string>>;
export function clean(text: unknown): string;
export function renderDataIssue(candidate: Candidate, opts: { tier: Tier; runDate: string; article?: { url?: string; inline?: boolean } | null; existingArticle?: Article | null; dedupNote: string }): { title: string; body: string; labels: string[] };
export function renderArticleIssue(candidate: Candidate, opts: { dataUrl: string; runDate: string; dedupNote: string }): { title: string; body: string; labels: string[] };
export function planFiling(candidates: Candidate[], opts: { issues: Issue[]; storeNames: Map<string, string>; articles: Article[]; articleAccess: boolean; runDate: string; maxPairs?: number }): { file: { candidate: Candidate; tier: Tier; existingArticle: Article | null; dedupNote: string }[]; skipped: { name: string; reason: string }[] };
export class Usage {
  byModel: Record<string, { input: number; output: number; cacheWrite: number; cacheRead: number; webSearches: number; webFetches: number }>;
  calls: number;
  add(model: string, usage: any): void;
  costOf(model: string): number;
  total(): number;
  table(): string;
}
export function renderSummary(input: { mode: string; runDate: string; usage: Usage; filed: any[]; skipped: { name: string; reason: string }[]; notes?: string[] }): string;
export function githubClient(token: string, fetchImpl?: typeof fetch): any;
export function parseBlogIndex(html: string, base?: string): Article[];
export interface Planned { name: string; tier: Tier; labels: string[]; title: string; data: { title: string; body: string; labels: string[] }; article: { title: string; body: string; labels: string[] } | null; dataUrl?: string; articleUrl?: string; articleNote?: string }
export function main(argv?: string[], env?: Record<string, string | undefined>, deps?: Record<string, any>): Promise<{ summary: string; planned: Planned[]; skipped?: { name: string; reason: string }[]; usage?: Usage }>;
