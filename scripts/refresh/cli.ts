import fs from "node:fs";
import { parseArgs } from "node:util";
import { z } from "zod";
import { RefreshStore, Update, digest } from "./store";

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: Object.fromEntries(
    [
      "cycle",
      "scope",
      "baseline",
      "retry-of",
      "scope-amendment",
      "id",
      "report",
      "status",
      "outcome",
      "url",
      "reason",
      "notes",
    ].map((k) => [k, { type: "string" as const }]),
  ),
});
const need = (name: string) => {
  const value = values[name];
  if (!value) throw Error(`Missing --${name}`);
  return value;
};
const store = new RefreshStore(process.cwd());
async function publicBytes(filename: string) {
  const response = await fetch(
    `https://rewire-it.web.app/${filename}?verify=${Date.now()}`,
    {
      redirect: "error",
      headers: { "Cache-Control": "no-cache" },
      signal: AbortSignal.timeout(15000),
    },
  );
  if (!response.ok || !response.body)
    throw Error(
      `Live publication metadata unavailable: HTTP ${response.status}`,
    );
  const chunks: Buffer[] = [];
  let bytes = 0;
  for await (const chunk of response.body as unknown as AsyncIterable<Uint8Array>) {
    bytes += chunk.length;
    if (bytes > 256 * 1024) throw Error("Publication metadata too large");
    chunks.push(Buffer.from(chunk));
  }
  return Buffer.concat(chunks);
}
async function main() {
  switch (positionals[0]) {
    case "begin":
      return store.begin(
        need("cycle"),
        need("scope").split(","),
        need("baseline"),
        values["retry-of"],
        values["scope-amendment"],
      );
    case "resume":
      return {
        run: store.get(need("id")),
        pr_url: store.link(need("id")),
        instruction:
          "Continue existing running attempt; terminal attempts require explicit begin --retry-of with the same cycle, scope and baseline.",
      };
    case "finish":
      return store.finish(
        need("id"),
        need("report"),
        z.enum(["completed", "blocked", "failed"]).parse(need("status")),
        z
          .enum(["no_change", "review_required"])
          .optional()
          .parse(values.outcome),
      );
    case "link-pr":
      store.linkPr(need("id"), need("url"));
      return { linked: need("url") };
    case "unlock":
      store.unlock(need("reason"));
      return { recovered: true };
    case "status":
      return store.status();
    case "check-due": {
      const status = store.status();
      if (status.alerts.length) process.exitCode = 2;
      return { schedule: status.schedule, alerts: status.alerts };
    }
    case "export": {
      const data = store.publicData();
      store.write("public/omics/refresh.json", data);
      return {
        exported: "public/omics/refresh.json",
        runs: data.runs.length,
        updates: data.updates.length,
      };
    }
    case "record-publication": {
      const notes = z
        .object({
          summary: z.array(z.string().min(1)).min(1),
          links: z.array(
            z.object({ label: z.string().min(1), url: z.string().url() }),
          ),
          maintenance_run_id: z.string().nullable(),
        })
        .strict()
        .parse(store.read(need("notes")));
      if (notes.maintenance_run_id) {
        const run = store.get(notes.maintenance_run_id);
        if (run.status !== "completed" || run.outcome !== "review_required")
          throw Error(
            "Publication attribution requires a completed candidate-change sweep",
          );
      }
      const before = await publicBytes("deployment.json"),
        manifest = await publicBytes("omics/manifest.json"),
        after = await publicBytes("deployment.json");
      if (!before.equals(after))
        throw Error("Live deployment changed while recording; retry");
      const receipt = JSON.parse(before.toString()),
        scientific = JSON.parse(manifest.toString());
      if (
        receipt.schema !== 1 ||
        receipt.release_id !== scientific.release_id ||
        digest(manifest) !== receipt.manifest_sha256
      )
        throw Error("Live deployment/manifest mismatch");
      const archive = fs.readFileSync(
        store.file(`data/omics/releases/${scientific.release_id}.json`),
      );
      if (!archive.equals(manifest))
        throw Error("Live release differs from immutable local archive");
      const proof = {
        observed_at: store.now(),
        origin: "https://rewire-it.web.app",
        deployment: receipt,
        manifest_sha256: digest(manifest),
      };
      const proofHash = digest(JSON.stringify(proof, null, 2) + "\n");
      const update = Update.parse({
        ...notes,
        release_id: receipt.release_id,
        manifest_sha256: receipt.manifest_sha256,
        commit: receipt.commit,
        published_at: proof.observed_at,
        time_basis: "observed",
        receipt_url: "https://rewire-it.web.app/deployment.json",
        proof_sha256: proofHash,
      });
      return store.locked(() => {
        const target = `maintenance/updates/${update.release_id}.json`;
        if (fs.existsSync(store.file(target)))
          throw Error(
            "Publication already recorded; immutable first observation",
          );
        store.write(
          `maintenance/publication-proofs/${proofHash}.json`,
          proof,
          true,
        );
        store.write(target, update, true);
        return update;
      });
    }
    default:
      throw Error(
        "Usage: npm run refresh -- status|check-due|begin|resume|finish|link-pr|export|record-publication|unlock (see docs/database-refresh.md)",
      );
  }
}
main()
  .then((v) => console.log(JSON.stringify(v, null, 2)))
  .catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  });
