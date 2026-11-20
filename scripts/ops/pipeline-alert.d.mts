export const LABEL: string;
export const ASSIGNEE: string;
export const LIVE_SOURCE: string;
export interface RunInfo {
  head_branch?: string; event?: string; conclusion?: string | null; path?: string; name?: string;
  repository?: { full_name?: string }; head_repository?: { full_name?: string } | null;
}
export interface PullRequestRuns { workflows?: string[]; branchPrefix?: string }
export type Outcome = "fail" | "pass" | "ignore";
export interface AlertState { failing: Record<string, { url: string; summary: string; since: string }> }
export interface Decision { action: "none" | "create" | "update" | "close"; title?: string; body?: string; comment?: string }
export function outcomeOf(run: RunInfo, prRuns?: PullRequestRuns): Outcome;
export function judgeJobs(jobs: { id: number; conclusion: string | null }[], timedOut?: Set<number>): "fail" | "ignore";
export function timedOutByAnnotations(annotations: { message?: string }[] | null | undefined): boolean;
export function sourceOf(run: RunInfo): string;
export function readState(body: string | null | undefined): AlertState;
export function renderBody(state: AlertState): string;
export function plan(input: {
  issue: { number?: number; body?: string | null } | null;
  source: string; outcome: Outcome; url: string; summary: string; details?: string; now: string;
}): Decision;
export function logExcerpt(log: string, lines?: number): string;
export function staleness(input: {
  liveId: string; releases: { tagName: string; publishedAt: string | null }[]; now: string; maxAgeHours?: number;
}): { stale: boolean; newest: string; ageHours: number };
export function main(argv?: string[], env?: Record<string, string | undefined>): Promise<void>;
