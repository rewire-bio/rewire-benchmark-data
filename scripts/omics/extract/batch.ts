/**
 * Turn one paper's comparison table into catalogue records.
 *
 * Every benchmark extractor produces the same shape: a pinned source, the tasks
 * the paper defines, the methods it ran, and one cell per method and task. This
 * builds the records that shape implies, so a new benchmark is a parser and a
 * description rather than another copy of the record layout.
 *
 * Three rules are enforced here rather than left to each extractor.
 *
 * A task reaches its benchmark only through a sourced claim, because the
 * catalogue will not roll results up over an unevidenced edge. Each task
 * therefore carries a claim naming the row or section that states it belongs to
 * the benchmark.
 *
 * A cell with no number is not a result. Papers write "-", "N/A" or a blank for
 * a method that does not apply, and emitting those as zero or as a missing
 * value would put a number in the catalogue that the paper does not contain.
 *
 * A figure compares one metric on one dataset. Panels are built per task, never
 * across tasks, because a mean over different metrics is not a score.
 */
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import type { MissingReason, uncertaintyTypes } from "../../../shared/omics/attributes";
import type { RecordEntry } from "../schema";
import type { PdfTransformation } from "./pdf";

/**
 * A missing value is an absent key plus a reason, not a null and not a token.
 *
 * The reasons come from data/vocab/missingness.ttl, and the fields named here
 * are declared for their kind in shared/omics/attribute-registry.ts.
 */
const missingFields = (reasons: Record<string, MissingReason>) =>
  Object.fromEntries(
    Object.entries(reasons).map(([field, reason]) => [field, { reason }]),
  );

/**
 * An id fragment.
 *
 * Plus and ampersand are spelled out rather than dropped: AbDPO and AbDPO++ are
 * different methods, and a slug reducing both to "abdpo" would file one
 * method's numbers under the other.
 */
export const slug = (value: string): string =>
  value
    .toLowerCase()
    .replace(/[‐-―−]/g, "-")
    .replace(/\+/g, "-plus-")
    .replace(/&/g, "-and-")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

export type SourceSpec = {
  id: string;
  /** False when the id names a source the catalogue already holds. The earlier
   * evidence sweep pinned most of these artifacts, and a second source record
   * for the same bytes would split one paper's provenance in two. */
  emit?: boolean;
  name: string;
  url: string;
  artifactUrl: string;
  sha256: string;
  version: string;
  venue: string;
  retrievedAt: string;
};

export type TaskSpec = {
  /** Short label used in ids and figure titles, such as "SSP" or "EC". */
  label: string;
  title: string;
  metric: string;
  metricKey: string;
  unit: string;
  direction: "higher" | "lower";
  dataset: string;
  /** Free text: split sizes, protocol notes, whatever the paper states. */
  protocol: string;
  locator: string;
};

export type MethodSpec = {
  name: string;
  /**
   * No "model" here on purpose. A bare model record is a 1.0 kind, and the
   * release requires every one of those to appear in the reviewed entity
   * classification map. What a comparison table holds is a method the authors
   * wrote or a published model as they configured it, which is what these
   * kinds say.
   */
  kind: "method" | "configuration" | "pipeline" | "service";
  description: string;
  locator: string;
};

export type CellSpec = {
  method: string;
  task: string;
  printed: string;
  value: string | null;
  sd?: string | null;
  locator: string;
};

export type BatchSpec = {
  key: string;
  /** Folder under data/omics that holds the batch. Defaults to the key. */
  batch?: string;
  benchmarkId: string;
  benchmarkName: string;
  area: string;
  source: SourceSpec;
  /** Who read the numbers, in free text. Recorded as review.reviewer_note. */
  reviewer: string;
  /** Agent concept keys for the reader (data/vocab/agent.ttl). */
  reviewerAgents?: string[];
  date: string;
  /** How the numbers were read, in free text. Recorded as review.method_note. */
  method: string;
  /** Review-method concept keys (data/vocab/review-method.ttl). */
  reviewMethods?: string[];
  /** Recorded when text is derived from a verified PDF during this run. */
  transformation?: PdfTransformation;
  /** Meaning of a printed ± spread, only when stated by the inspected source. */
  uncertaintyType?: (typeof uncertaintyTypes)[number];
  /** What the batch does not claim, recorded on every figure. */
  caveats: string[];
  tasks: TaskSpec[];
  methods: MethodSpec[];
  cells: CellSpec[];
};

const id = (spec: BatchSpec, kind: string, ...parts: string[]) =>
  [spec.key, kind, ...parts.map(slug)].join("-");

export function buildBatch(spec: BatchSpec): RecordEntry[] {
  const areas = [spec.area];
  const sourceId = spec.source.id;
  const taskByLabel = new Map(spec.tasks.map((t) => [t.label, t]));
  const methodByName = new Map(spec.methods.map((m) => [m.name, m]));
  const out: RecordEntry[] = [];
  const reviewMethods = spec.reviewMethods ?? ["automated-source-review"];
  const reviewerAgents = spec.reviewerAgents ?? ["unidentified-automated-reviewer"];

  if (spec.source.emit !== false)
    out.push({
      id: sourceId,
      kind: "source",
    name: spec.source.name,
      description:
        "Pinned primary artifact. Review is limited to the cited rows.",
      status: "source_checked",
      facets: { areas },
      source_ids: [],
      links: [],
      attributes: {
        url: spec.source.url,
        artifact_url: spec.source.artifactUrl,
        artifact_sha256: spec.source.sha256,
        retrieved_at: spec.source.retrievedAt,
        venue: spec.source.venue,
        version: spec.source.version,
      },
    });

  const datasetId = (name: string) => id(spec, "dataset", name);
  for (const name of [...new Set(spec.tasks.map((t) => t.dataset))])
    out.push({
      id: datasetId(name),
      kind: "dataset_subset",
      name: `${name} (${spec.benchmarkName} split)`,
      description: `The split of ${name} that ${spec.benchmarkName} evaluated on. The upstream dataset release is not catalogued here, so no claim is made that this matches its original splits.`,
      status: "source_checked",
      facets: { areas },
      source_ids: [sourceId],
      links: [],
      attributes: {
        missing_metadata: missingFields({
          version: "unreported",
          url: "unextracted",
        }),
      },
    });

  // Papers are not always consistent about capitalising their own model names:
  // NABench prints both GenSLM and GenSlm. Those are one entity. Names that
  // differ by more than case are not, so a real collision fails here instead of
  // silently merging two methods into one row.
  const byMethodId = new Map<string, MethodSpec>();
  for (const method of spec.methods) {
    const key = id(spec, "method", method.name);
    const seen = byMethodId.get(key);
    if (!seen) byMethodId.set(key, method);
    else if (seen.name.toLowerCase() !== method.name.toLowerCase())
      throw new Error(
        `Methods "${seen.name}" and "${method.name}" collide on ${key}`,
      );
  }
  const methodName = (printed: string) =>
    byMethodId.get(id(spec, "method", printed))!.name;

  for (const method of byMethodId.values())
    out.push({
      id: id(spec, "method", method.name),
      kind: method.kind,
      name: method.name,
      description: method.description,
      status: "source_checked",
      facets: { areas },
      source_ids: [sourceId],
      links: [],
      attributes: {
        source_locator: method.locator,
        missing_metadata: missingFields({
          checkpoint_revision: "unreported",
          parameters: "unextracted",
        }),
      },
    });

  const scored = spec.cells.filter((cell) => cell.value !== null);
  for (const task of spec.tasks) {
    const taskId = id(spec, "task", task.label);
    const rows = scored.filter((cell) => cell.task === task.label);
    const resultIds = rows.map((cell) =>
      id(spec, "result", cell.method, task.label, task.metricKey),
    );
    out.push({
      id: taskId,
      kind: "task",
      name: `${spec.benchmarkName} ${task.label}: ${task.title}`,
      description: `${task.title}. Scored with ${task.metric} on ${task.dataset}. ${task.protocol}`,
      status: "source_checked",
      facets: { areas, tasks: [task.title] },
      source_ids: [sourceId],
      links: [{ relation: "part_of", target_id: spec.benchmarkId }],
      attributes: {
        metric: task.metricKey,
        metric_direction: task.direction,
        dataset: task.dataset,
        protocol: task.protocol,
        source_locator: task.locator,
        ...(resultIds.length >= 2
          ? {
              comparison_panels: [
                {
                  id: id(spec, "panel", task.label),
                  title: `${spec.benchmarkName} ${task.label}: ${task.title}`,
                  protocol_id: taskId,
                  dataset_id: datasetId(task.dataset),
                  metric: task.metricKey,
                  unit: task.unit,
                  direction: task.direction,
                  result_ids: resultIds,
                  source_ids: [sourceId],
                  source_locator: task.locator,
                  context: `Every method ${spec.benchmarkName} reports on ${task.title}, scored with ${task.metric} on ${task.dataset}.`,
                  caveats: spec.caveats,
                  review: { method: "automated_source_review", date: spec.date },
                },
              ],
            }
          : {}),
      },
    });
    out.push({
      id: id(spec, "association", task.label),
      kind: "claim",
      name: `${spec.benchmarkName} ${task.label}: part of ${spec.benchmarkId}`,
      description: `The source lists ${task.label} among the tasks that make up ${spec.benchmarkName}.`,
      status: "source_checked",
      facets: { areas },
      source_ids: [sourceId],
      links: [{ relation: "subject", target_id: taskId }],
      attributes: {
        field: `links:part_of:${spec.benchmarkId}`,
        target_id: spec.benchmarkId,
        source_locator: task.locator,
        review: {
          method: reviewMethods,
          date: spec.date,
          note: "Primary-source transcription with no human sign-off and no independent reproduction.",
        },
      },
    });
  }

  for (const cell of scored) {
    const task = taskByLabel.get(cell.task);
    const method = methodByName.get(cell.method);
    if (!task) throw new Error(`Cell names an unknown task: ${cell.task}`);
    if (!method) throw new Error(`Cell names an unknown method: ${cell.method}`);
    const evaluationId = id(spec, "evaluation", cell.method, task.label);
    out.push({
      id: evaluationId,
      kind: "evaluation",
      name: `${methodName(cell.method)} on ${spec.benchmarkName} ${task.label}: ${task.title}`,
      description: `${spec.benchmarkName} evaluation of ${methodName(cell.method)} on ${task.title}, scored with ${task.metric}.`,
      status: "source_checked",
      facets: { areas, tasks: [task.title] },
      source_ids: [sourceId],
      links: [
        { relation: "assessment", target_id: id(spec, "task", task.label) },
        { relation: "system", target_id: id(spec, "method", cell.method) },
        { relation: "data", target_id: datasetId(task.dataset) },
      ],
      attributes: {
        origin: "author_reported",
        protocol: task.protocol,
        comparison: {
          protocol_id: id(spec, "task", task.label),
          metric_implementation: task.metric,
        },
        missing_metadata: missingFields({
          checkpoint_revision: "unreported",
          seeds: "unreported",
          budget: "unreported",
          split_manifest: "unextracted",
        }),
        source_locator: cell.locator,
      },
    });
    out.push({
      id: id(spec, "result", cell.method, task.label, task.metricKey),
      kind: "result",
      name: `${cell.method} · ${spec.benchmarkName} ${task.label} · ${task.metric}`,
      description:
        "Author-reported score transcribed from the paper's comparison table. Source checked; not independently reproduced.",
      status: "source_checked",
      facets: { areas, tasks: [task.title] },
      source_ids: [sourceId],
      links: [{ relation: "evaluation", target_id: evaluationId }],
      attributes: {
        metric: task.metricKey,
        metric_direction: task.direction,
        unit: task.unit,
        printed_value: cell.printed,
        numeric_value: cell.value,
        // A printed ± spread whose meaning the source does not state is an
        // unresolved spread, not a standard deviation. A cell with no spread
        // carries no uncertainty key at all, and says why in missing_metadata.
        ...(cell.sd
          ? {
              uncertainty: {
                type: spec.uncertaintyType ?? "unresolved_spread",
                value: cell.sd,
              },
            }
          : {}),
        source_locator: cell.locator,
        missing_metadata: missingFields({
          denominator: "unextracted",
          seeds: "unreported",
          ...(cell.sd ? {} : { uncertainty: "unextracted" as const }),
        }),
        review: {
          method: reviewMethods,
          method_note: spec.method,
          reviewer: reviewerAgents,
          reviewer_note: spec.reviewer,
          date: spec.date,
          artifact_sha256: spec.source.sha256,
          retrieval_url: spec.source.artifactUrl,
          note: "Source checked, not reproduced. Metrics differ by task, so no composite score across tasks is computed or implied.",
        },
      },
    });
  }
  return out;
}

/**
 * Write the batch folder: the records and the receipt beside them.
 *
 * The receipt records what the extraction did and leaves the review fields
 * empty, because review is a separate pass by another worker. `npm run batch --
 * hash` fills in files and source_artifacts, and the reviewer fills the rest.
 * `root` exists so a test can write to a temporary directory.
 */
export function writeBatch(spec: BatchSpec, root = "data/omics"): RecordEntry[] {
  const records = buildBatch(spec);
  const batch = spec.batch ?? spec.key;
  const folder = path.join(root, batch);
  fs.mkdirSync(folder, { recursive: true });
  const file = path.join(folder, "batch.jsonl");
  const receipt = path.join(folder, "review.json");
  fs.writeFileSync(
    file,
    records.map((record) => JSON.stringify(record)).join("\n") + "\n",
  );
  const held = fs.existsSync(receipt)
    ? (JSON.parse(fs.readFileSync(receipt, "utf8")) as Record<string, unknown>)
    : {};
  fs.writeFileSync(
    receipt,
    JSON.stringify(
      {
        schema_version: "1.0",
        method: null,
        review_methods: [],
        reviewer: null,
        reviewed_at: null,
        scope: null,
        limitations: [],
        errors: [],
        ...held,
        extraction: {
          batch,
          benchmark: spec.benchmarkId,
          source: spec.source.artifactUrl,
          artifact_sha256: spec.source.sha256,
          records_sha256: createHash("sha256")
            .update(fs.readFileSync(file))
            .digest("hex"),
          ...(spec.transformation
            ? { transformation: spec.transformation }
            : {}),
          method: spec.method,
          extracted_by: spec.reviewer,
          extracted_at: spec.date,
        },
      },
      null,
      2,
    ) + "\n",
  );
  const counts = records.reduce<Record<string, number>>((acc, record) => {
    acc[record.kind] = (acc[record.kind] || 0) + 1;
    return acc;
  }, {});
  console.log(`${file}: ${records.length} records`, counts);
  return records;
}
