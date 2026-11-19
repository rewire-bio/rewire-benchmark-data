/** How the question gets asked, and why no test ever asks it for real.
 *
 * The transport is one function, injected. The stage builds a request, hands it over and reads
 * a string back; it does not know whether that string came from a network, a recorded fixture
 * or a file somebody wrote by hand. That is what lets every test run offline: a test passes a
 * transport that answers from a recording keyed by the request's own digest, and a request the
 * recording does not hold is an error rather than a call.
 *
 * The live path is a dynamic import and a call-time environment read, both on purpose.
 * Importing this module must never require the client library to be installed or a key to be
 * set, because `shared/omics/extract/index.ts` is imported by commands that ask nothing at
 * all. A missing key is reported at the call, by name, in one sentence.
 */
import { createHash } from "node:crypto";
import { canonicalJson } from "../../../archive/layers/grid/index";

/** The identifier recorded on every receipt. A fact about what ran, not an attribution. */
export const DEFAULT_MODEL = "claude-opus-5-5";
/** Deciding which of fifteen records a caption names is a short reading task, so the request
 * asks for the shallow end of the reasoning range. The level is recorded on the receipt
 * because changing it changes what ran. */
export const DEFAULT_EFFORT = "low";
/** Four short fields. The ceiling is here to bound a reply that goes wrong, not to shape one. */
export const DEFAULT_MAX_TOKENS = 2000;
/** The environment variable the live path reads, named once so the error can name it. */
export const KEY_VARIABLE = "ANTHROPIC_API_KEY";

/** The client library, named in a constant rather than written into the import.
 *
 * `scripts/agents/package.json` holds this dependency and says why it is not in the root
 * package: so the data checks do not install it. Nothing in this lane needs it either, because
 * every test runs against a recording and the deterministic pass calls nothing. Naming it here
 * keeps it out of the root's dependency graph and out of the type checker's resolution, and
 * the import below turns its absence into a sentence rather than a stack trace. */
export const CLIENT_PACKAGE = "@anthropic-ai/sdk";

export interface LabelRequest {
  model: string;
  effort: string;
  max_tokens: number;
  /** The prompt file's bytes. */
  system: string;
  /** The rendered question for one table. */
  question: string;
  /** JSON Schema for the reply, so the shape is a property of the request. */
  schema: unknown;
}

export interface LabelReply {
  /** The reply, as text. Reading it into an answer is `answer.ts`, never a transport. */
  text: string;
  /** The identifier the service reports having answered with, which is not always the one
   * asked for and is what the receipt records. */
  model: string;
  input_tokens: number | null;
  output_tokens: number | null;
}

export type LabelTransport = (request: LabelRequest) => Promise<LabelReply>;

/** The digest a recording is keyed by: every field of the request, canonically ordered.
 *
 * Keyed on the whole request rather than on the table, so a recording cannot answer a question
 * that differs from the one it was made for. A changed prompt, a changed shortlist or a
 * changed model gives a different key and a missing recording, which is a loud test failure
 * rather than a quiet wrong answer. */
export const requestDigest = (request: LabelRequest): string =>
  createHash("sha256").update(canonicalJson(request as unknown as Record<string, unknown>)).digest("hex");

/**
 * A transport that answers from a recording and never opens a socket.
 *
 * `replies` maps a request digest to the reply. A string is taken as the reply text, with the
 * request's own model and no token counts, which is what a hand-written fixture wants to say.
 */
export function recordedTransport(replies: Record<string, LabelReply | string>): LabelTransport {
  return async (request) => {
    const key = requestDigest(request);
    const held = replies[key];
    if (held === undefined)
      throw new Error(
        `No recorded reply for request ${key.slice(0, 16)}. A recording is made for one exact request: prompt, question, shortlist, model and all.`,
      );
    return typeof held === "string"
      ? { text: held, model: request.model, input_tokens: null, output_tokens: null }
      : held;
  };
}

/** What the live transport sends, kept out of the function so a test can assert the shape
 * without a client library. The sampling controls ADR 0002 decision 5 names are not here:
 * the current API rejects `temperature`, and `effort` is the control that replaced it. */
export function liveBody(request: LabelRequest): Record<string, unknown> {
  return {
    model: request.model,
    max_tokens: request.max_tokens,
    system: request.system,
    messages: [{ role: "user", content: request.question }],
    output_config: { effort: request.effort, format: { type: "json_schema", schema: request.schema } },
  };
}

/** A minimal view of the client this module calls, so the live path can be exercised against a
 * double without the library present. */
export interface MessagesClient {
  messages: { create(body: Record<string, unknown>): Promise<{ content: unknown[]; model?: string; usage?: { input_tokens?: number; output_tokens?: number } }> };
}

/** The text blocks of a reply, joined. A structured reply is one text block; joining is for the
 * case where it is not, so the failure is a schema failure in `answer.ts` and not a silent
 * half-read reply. */
export function textOf(content: unknown[]): string {
  return content
    .filter((block): block is { type: string; text: string } => typeof block === "object" && block !== null && (block as { type?: string }).type === "text")
    .map((block) => block.text)
    .join("");
}

/**
 * The transport that asks for real.
 *
 * `client` is for a caller that already holds one. Without it the client library is imported
 * when the first question is asked, so a command that labels nothing needs neither the library
 * nor a key.
 */
export function liveTransport(options: { client?: MessagesClient; env?: NodeJS.ProcessEnv } = {}): LabelTransport {
  return async (request) => {
    let client = options.client;
    if (!client) {
      const env = options.env ?? process.env;
      const key = env[KEY_VARIABLE];
      if (!key || key.trim() === "")
        throw new Error(`${KEY_VARIABLE} is not set, so the label stage cannot ask anything. Set it, or run without the label stage.`);
      const loaded = (await import(CLIENT_PACKAGE).catch((error: Error) => {
        throw new Error(`The label stage needs the ${CLIENT_PACKAGE} package, which is not installed here: ${error.message}`);
      })) as { default: new (options: Record<string, unknown>) => MessagesClient };
      client = new loaded.default({ apiKey: key, maxRetries: 3, timeout: 5 * 60 * 1000 });
    }
    const reply = await client.messages.create(liveBody(request));
    return {
      text: textOf(reply.content ?? []),
      model: reply.model ?? request.model,
      input_tokens: reply.usage?.input_tokens ?? null,
      output_tokens: reply.usage?.output_tokens ?? null,
    };
  };
}
