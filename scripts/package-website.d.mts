export interface PreparedWebsiteFile {
  source: string;
  destination: string;
  sha256: string;
  bytes: number;
  scope: 'current' | 'historical';
}
export interface PreparedWebsiteManifest {
  schema_version: 1;
  release_id: string;
  files: PreparedWebsiteFile[];
}
export function packageWebsite(options?: {
  dataDir?: string;
  outputDir?: string;
  currentOnly?: boolean;
}): Promise<{ manifest: PreparedWebsiteManifest; manifestPath: string; filesCount: number }>;
