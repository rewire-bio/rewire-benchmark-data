// A client for rdf-kg-mcp (rewire-bio/rdf-kg-mcp), the MCP server that loads a KG bundle. The
// intake and reviewer agents start it over stdio with the draft tools on (serve --drafts), search
// the release for possible duplicates and link targets, write new records to the server's draft
// overlay and export them as a batch for `npm run records -- add`. For an entity-update issue the
// server is also given the store's entity lines (--draft-records), and the change to an existing
// record goes through draft_change and comes back as changes.jsonl for
// `npm run records -- change <review> <batch-dir> --changes <file>` (rdf-kg-mcp #10). The overlay is
// advisory; records add and records change in the pull request are the gate. Nothing here writes to
// the KG: the KG is never the store.
//
// The server and its bundle come from the workflow (.github/workflows/intake.yml):
//   KG_BUNDLE        the bundle (.tar.gz, directory or manifest) of the latest kg/<id> release
//   KG_DRAFT_CONFIG  the draft block for this checkout (npm run kg -- draft-block <file>), because
//                    bundles built before #325 carry none
//   KG_MCP_COMMAND   the server command (default rdf-kg-mcp, installed with uv tool install)
// Without KG_BUNDLE, or when the server does not start, startKg returns { kg: null, error } and
// the agents fall back to the checks they ran before (#255).

import { existsSync, mkdirSync, readFileSync } from 'node:fs';

export const START_TIMEOUT_MS = 180000;
export const CALL_TIMEOUT_MS = 60000;

/**
 * Parse an MCP tool result: the structured content, else the JSON text. Throws on a tool error,
 * with `refused` set: the server answered and refused the call. A timeout or a lost connection
 * throws from callTool without it.
 */
export function toolResult(name, result) {
  const text = (result?.content ?? []).filter((c) => c.type === 'text').map((c) => c.text).join('\n');
  if (result?.isError) throw Object.assign(new Error(`${name}: ${text.slice(0, 500) || 'tool error'}`), { refused: true });
  if (result?.structuredContent && typeof result.structuredContent === 'object') {
    // FastMCP wraps a non-object return as { result }.
    const s = result.structuredContent;
    return Object.keys(s).length === 1 && 'result' in s ? s.result : s;
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/** Peak resident memory in MB of a process (Linux /proc only), or null. */
export function peakMemoryMb(pid) {
  try {
    const status = readFileSync(`/proc/${pid}/status`, 'utf8');
    const kb = Number(/VmHWM:\s+(\d+)\s+kB/.exec(status)?.[1]);
    return kb ? Math.round(kb / 1024) : null;
  } catch {
    return null;
  }
}

/**
 * Wrap an MCP client (anything with callTool({ name, arguments })) as the calls the agents use.
 * `config` is the draft block: it maps each record kind to its class, for the `types` filter of
 * search, and gives the IRI base.
 */
export function kgApi(client, { config, stats = { calls: {}, ms: 0 }, close = async () => {}, pid = null } = {}) {
  const call = async (name, args = {}) => {
    const t = Date.now();
    stats.calls[name] = (stats.calls[name] ?? 0) + 1;
    try {
      const result = await client.callTool({ name, arguments: args }, undefined, { timeout: CALL_TIMEOUT_MS });
      return toolResult(name, result);
    } finally {
      stats.ms += Date.now() - t;
    }
  };
  const kinds = config?.kinds ?? {};
  const iriBase = config?.iri_base ?? '';
  const kindOfClass = new Map(Object.entries(kinds).map(([kind, cls]) => [cls, kind]));
  return {
    config,
    stats,
    pid,
    /** The class of a record kind, as the draft block names it (a prefixed name). */
    classOf: (kind) => kinds[kind] ?? null,
    /** The record kind of a class from a search hit (prefixed name or IRI), or null. */
    kindOfClass: (cls) => kindOfClass.get(cls) ?? null,
    iriOf: (id) => `${iriBase}${id}`,
    /** The record id of an IRI under the draft block's base, or null. */
    idOf: (iri) => (iriBase && String(iri).startsWith(iriBase) ? String(iri).slice(iriBase.length) : null),
    search: (text, { kinds: ks = [], limit = 10 } = {}) =>
      call('search', { text, limit, ...(ks.length ? { types: ks.map((k) => kinds[k]).filter(Boolean) } : {}) }),
    describe: (iri, { limit = 40, direction = 'out' } = {}) => call('describe_resource', { iri, direction, limit }),
    upsert: (record) => call('draft_upsert', { record }),
    /** Change fields of a store record: JSON Pointer changes against the digest of its committed line. */
    change: (id, changes, baseSha256) => call('draft_change', { id, changes, base_sha256: baseSha256 }),
    remove: (id) => call('draft_remove', { id }),
    diff: () => call('draft_diff'),
    exportBatch: () => call('draft_export'),
    close,
  };
}

/**
 * Start rdf-kg-mcp over stdio and connect to it. With `draftConfig` (a draft block file) the draft
 * tools are on, and `draftRecords` (store files or folders) lets draft_change change those records; with only `config` ({ iri_base, kinds }, for search filters) the server is
 * read-only, as the reviewer uses it. Returns { kg, error }: kg is null when there is no bundle or
 * the server fails to start within the timeout, and the caller falls back.
 * `deps.connect` replaces the server in tests: (options) => { client, close, pid }.
 */
export async function startKg({ bundle, draftConfig = '', draftDir = '', draftRecords = [], config: readOnlyConfig = null, command = 'rdf-kg-mcp', cacheDir = '', timeoutMs = START_TIMEOUT_MS, log = () => {} }, deps = {}) {
  if (!bundle) return { kg: null, error: 'no KG bundle given (KG_BUNDLE)' };
  if (!deps.connect && !/^https:\/\//.test(bundle) && !existsSync(bundle)) return { kg: null, error: `KG bundle ${bundle} not found` };
  if (!readOnlyConfig && (!draftConfig || !existsSync(draftConfig))) return { kg: null, error: `draft config ${draftConfig || '(none)'} not found` };
  const config = readOnlyConfig ?? JSON.parse(readFileSync(draftConfig, 'utf8'));
  const args = ['serve', bundle, '--store', 'memory', '--query-timeout', '0'];
  if (!readOnlyConfig) {
    mkdirSync(draftDir, { recursive: true });
    args.push('--drafts', '--draft-dir', draftDir, '--draft-config', draftConfig);
    for (const path of draftRecords) args.push('--draft-records', path);
  }
  const started = Date.now();
  let timer;
  let pending;
  try {
    const connect = deps.connect ?? (async () => {
      const { Client } = await import('@modelcontextprotocol/sdk/client/index.js');
      const { StdioClientTransport } = await import('@modelcontextprotocol/sdk/client/stdio.js');
      const transport = new StdioClientTransport({
        command,
        args,
        env: { ...process.env, ...(cacheDir ? { RDF_KG_MCP_CACHE: cacheDir } : {}) },
        stderr: 'pipe',
      });
      // The server logs loading progress to stderr; keep the tail for a failure message.
      let tail = '';
      transport.stderr?.on('data', (chunk) => {
        tail = `${tail}${chunk}`.slice(-2000);
      });
      const client = new Client({ name: 'rewire-agents', version: '1.0.0' });
      try {
        await client.connect(transport);
      } catch (e) {
        throw new Error(`${e?.message ?? e}${tail ? `; server said: ${tail.trim().split('\n').slice(-3).join(' | ')}` : ''}`);
      }
      return { client, pid: transport.pid, close: () => client.close() };
    });
    pending = connect({ command, args });
    // A server that becomes ready after the timeout is closed, so it does not keep the run alive.
    pending.catch(() => {});
    const conn = await Promise.race([
      pending,
      new Promise((_, reject) => {
        timer = setTimeout(() => reject(new Error(`the server was not ready after ${Math.round(timeoutMs / 1000)} s`)), timeoutMs);
      }),
    ]);
    clearTimeout(timer);
    const stats = { calls: {}, ms: 0, readySeconds: 0, peakMemoryMb: null };
    const kg = kgApi(conn.client, {
      config,
      stats,
      pid: conn.pid ?? null,
      close: async () => {
        if (conn.pid) stats.peakMemoryMb = peakMemoryMb(conn.pid);
        try {
          await conn.close();
        } catch {
          // The process is gone either way.
        }
      },
    });
    // The first call proves the graph loaded; dataset_info is cheap.
    const info = await conn.client.callTool({ name: 'dataset_info', arguments: {} }, undefined, { timeout: CALL_TIMEOUT_MS }).then((r) => toolResult('dataset_info', r));
    stats.readySeconds = Math.round((Date.now() - started) / 100) / 10;
    stats.release = info?.release_id ?? info?.version ?? null;
    stats.statements = info?.graphs ? Object.values(info.graphs).reduce((n, g) => n + (Number(g?.statements ?? g?.size ?? 0) || 0), 0) || null : null;
    log(`KG server ready in ${stats.readySeconds} s (release ${stats.release ?? 'unknown'})`);
    return { kg, error: null };
  } catch (e) {
    clearTimeout(timer);
    if (pending) pending.then((c) => c.close()).catch(() => {});
    return { kg: null, error: String(e?.message ?? e).slice(0, 400) };
  }
}

// ---------- Changes to existing records (rdf-kg-mcp #10) ----------

const isObject = (v) => v !== null && typeof v === 'object' && !Array.isArray(v);
const pointer = (tokens) => `/${tokens.map((t) => String(t).replace(/~/g, '~0').replace(/\//g, '~1')).join('/')}`;

/**
 * Leaf-level differences between two records, as rdf-kg-mcp's draft_diff gives them:
 * { path (JSON Pointer), change: added | removed | changed, before?, after? }. Objects are compared
 * key by key (keys of `before` first, in its order, then keys only `after` has); anything else,
 * lists included, as a whole by its JSON text. Key order alone is no change.
 */
export function fieldDiff(before, after, path = []) {
  if (isObject(before) && isObject(after)) {
    const out = [];
    for (const key of [...Object.keys(before), ...Object.keys(after).filter((k) => !(k in before))]) {
      if (!(key in after)) out.push({ path: pointer([...path, key]), change: 'removed', before: before[key] });
      else if (!(key in before)) out.push({ path: pointer([...path, key]), change: 'added', after: after[key] });
      else out.push(...fieldDiff(before[key], after[key], [...path, key]));
    }
    return out;
  }
  if (JSON.stringify(before) === JSON.stringify(after)) return [];
  return [{ path: path.length ? pointer(path) : '/', change: 'changed', before, after }];
}

/** The draft_change changes that turn `before` into `after`: a set per added or changed leaf, a remove per removed key. */
export const changeOps = (before, after) =>
  fieldDiff(before, after).map((d) => (d.change === 'removed' ? { path: d.path, remove: true } : { path: d.path, value: d.after }));
