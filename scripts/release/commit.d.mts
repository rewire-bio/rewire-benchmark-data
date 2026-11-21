export function commitRelease(options: {
  releaseId: string;
  cwd?: string;
  attempts?: number;
  wait?: (attempt: number) => Promise<unknown>;
  log?: (message: string) => void;
}): Promise<{ release: string; built: string; main: string }>;
export function verifyReleaseCommit(options: { commit: string; tags?: string[]; cwd?: string }): { release: string; built: string };
