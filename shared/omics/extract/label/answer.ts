/** What the stage is allowed to say back, and the schema that holds it to it.
 *
 * Four fields, no prose to parse. The id is a choice from a list, not free text, so an id that
 * names nothing in the store is a refusal here rather than a lookup failure three stages
 * later. The quote is the evidence, and it is what every check in `check.ts` is run against.
 * The confidence is a claim the quote has to carry.
 *
 * The schema is declared twice on purpose: once in zod, which validates what came back, and
 * once as JSON Schema, which is what the request sends so that what comes back is the right
 * shape in the first place. They are checked against each other in the tests rather than
 * generated from one another, because the generated form of a four-field object is longer than
 * the object.
 */
import { z } from "zod";

/** The word that means the stage could not tell. It is a value of `record_id` rather than a
 * separate field so that an answer has exactly one place to say what it decided, and a reply
 * that omits the decision fails the schema instead of defaulting to one. */
export const NONE = "none";

export const confidences = ["high", "medium", "low"] as const;
export type Confidence = (typeof confidences)[number];

export const answerSchema = z
  .object({
    /** An id copied from the shortlist, or `NONE`. */
    record_id: z.string().min(1),
    /** Text copied from the table's printed caption or label, verbatim. Empty for `NONE`. */
    quote: z.string(),
    confidence: z.enum(confidences),
    /** One sentence. Recorded, never parsed. */
    reason: z.string().min(1),
  })
  .strict();
export type Answer = z.infer<typeof answerSchema>;

/** The same shape as JSON Schema, for `output_config.format`. `additionalProperties: false`
 * with every field required is what makes the reply's shape a property of the request rather
 * than something to hope for. */
export const answerJsonSchema = {
  type: "object",
  properties: {
    record_id: { type: "string", description: "An id copied from the shortlist, or the word none." },
    quote: { type: "string", description: "Words copied verbatim from the caption shown, empty when the answer is none." },
    confidence: { type: "string", enum: [...confidences] },
    reason: { type: "string", description: "One sentence." },
  },
  required: ["record_id", "quote", "confidence", "reason"],
  additionalProperties: false,
} as const;

/** Read a reply into an answer, or say why it is not one. The reply is text because that is
 * what a transport returns and what a recorded fixture holds; nothing downstream sees the
 * untyped form. */
export function readAnswer(text: string): { ok: true; answer: Answer } | { ok: false; detail: string } {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (error) {
    return { ok: false, detail: `the reply is not JSON: ${(error as Error).message}` };
  }
  const read = answerSchema.safeParse(parsed);
  if (!read.success) return { ok: false, detail: read.error.issues.map((issue) => `${issue.path.join(".")}: ${issue.message}`).join("; ") };
  return { ok: true, answer: read.data };
}
