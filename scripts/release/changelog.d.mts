export function pullRequestLines(log: string): string[];
export function changelogSince(since: string): string[] | null;
export function previousSource(config: { source_revision?: string }, configFile: string): string | null;
export function head(): string;
