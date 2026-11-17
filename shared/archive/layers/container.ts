/** Containers: gzip, tar and zip expanded to their members.
 *
 * A container is not a text layer and never gets one. It produces one
 * archive-member object per member, keyed on that member's own sha256, and
 * each member is then classified in its own right. A gzipped PDF is therefore
 * three objects: the container, the member and the member's text layer. That
 * is what lets a later claim cite a span in the PDF rather than in the
 * compressed file nobody can address.
 *
 * No archive library is in this repository's dependencies, so the readers
 * below are minimal and deliberately narrow. Anything they do not understand
 * is reported as a problem, never guessed at.
 */
import { createHash } from "node:crypto";
import zlib from "node:zlib";

const digest = (bytes: Buffer): string => createHash("sha256").update(bytes).digest("hex");

export interface Member {
  /** The member's path inside the container, as the container records it. */
  path: string;
  bytes: Buffer;
  sha256: string;
}

export interface Expansion {
  kind: "gzip" | "tar" | "zip";
  members: Member[];
  /** What could not be read, one line each. A container with problems still
   * returns the members it could read. */
  problems: string[];
}

export interface Limits {
  maxMembers: number;
  maxMemberBytes: number;
  maxTotalBytes: number;
}

export const defaultLimits: Limits = {
  maxMembers: 1024,
  maxMemberBytes: 64 * 1024 * 1024,
  maxTotalBytes: 256 * 1024 * 1024,
};

/** The name a gzip header carries, when it carries one. */
function gzipName(input: Buffer): string {
  if (input.length < 10 || input[0] !== 0x1f || input[1] !== 0x8b) return "";
  const flags = input[3];
  if ((flags & 0x08) === 0) return "";
  let at = 10;
  if (flags & 0x04) {
    if (at + 2 > input.length) return "";
    at += 2 + input.readUInt16LE(at);
  }
  const end = input.indexOf(0, at);
  if (end < 0) return "";
  return input.subarray(at, end).toString("latin1");
}

function expandGzip(input: Buffer, limits: Limits): Expansion {
  try {
    const bytes = zlib.gunzipSync(input, { maxOutputLength: limits.maxMemberBytes });
    // gzip -n records no name, which most of the committed artifacts were
    // written with, so a nameless member is called content.
    return { kind: "gzip", members: [{ path: gzipName(input) || "content", bytes, sha256: digest(bytes) }], problems: [] };
  } catch (error) {
    return { kind: "gzip", members: [], problems: [`gzip expansion failed: ${(error as Error).message}`] };
  }
}

const octal = (field: Buffer): number => {
  const text = field.toString("latin1").replace(/\0.*$/, "").trim();
  if (!text) return 0;
  const value = Number.parseInt(text, 8);
  return Number.isFinite(value) && value >= 0 ? value : -1;
};

function expandTar(input: Buffer, limits: Limits): Expansion {
  const members: Member[] = [];
  const problems: string[] = [];
  let total = 0;
  let at = 0;
  let longName: string | null = null;
  while (at + 512 <= input.length) {
    const header = input.subarray(at, at + 512);
    if (header.every((byte) => byte === 0)) break;
    const rawName = header.subarray(0, 100).toString("utf8").replace(/\0.*$/, "");
    const prefix = header.subarray(345, 500).toString("utf8").replace(/\0.*$/, "");
    const size = octal(header.subarray(124, 136));
    const type = String.fromCharCode(header[156] || 0x30);
    if (size < 0) {
      problems.push(`tar header at offset ${at} has an unreadable size field`);
      break;
    }
    const start = at + 512;
    const end = start + size;
    if (end > input.length) {
      problems.push(`tar member ${rawName || "(unnamed)"} runs past the end of the archive`);
      break;
    }
    at = start + Math.ceil(size / 512) * 512;
    if (type === "L") {
      longName = input.subarray(start, end).toString("utf8").replace(/\0.*$/, "");
      continue;
    }
    const name = longName ?? (prefix ? `${prefix}/${rawName}` : rawName);
    longName = null;
    if (type !== "0" && type !== "\0") continue;
    if (members.length >= limits.maxMembers) {
      problems.push(`tar holds more than ${limits.maxMembers} members; the rest were not read`);
      break;
    }
    if (size > limits.maxMemberBytes) {
      problems.push(`tar member ${name} is ${size} bytes, over the ${limits.maxMemberBytes} byte member limit`);
      continue;
    }
    total += size;
    if (total > limits.maxTotalBytes) {
      problems.push(`tar expands past the ${limits.maxTotalBytes} byte total limit at member ${name}`);
      break;
    }
    const bytes = Buffer.from(input.subarray(start, end));
    members.push({ path: name, bytes, sha256: digest(bytes) });
  }
  return { kind: "tar", members, problems };
}

/** The end of central directory record, searched from the end because a zip
 * may carry a trailing comment. */
function endOfCentralDirectory(input: Buffer): number {
  const earliest = Math.max(0, input.length - 65557 - 22);
  for (let at = input.length - 22; at >= earliest; at -= 1) {
    if (input.readUInt32LE(at) === 0x06054b50) return at;
  }
  return -1;
}

/** The member names in a zip's central directory, without expanding a byte.
 * An Office Open XML or OpenDocument package is a zip, and the member that
 * says so is not always the first one: three of the committed packages begin
 * with xl/drawings or docProps. An empty list means the directory could not
 * be read. */
export function zipEntryNames(input: Buffer, limit = 64): string[] {
  const names: string[] = [];
  const eocd = endOfCentralDirectory(input);
  if (eocd < 0) return names;
  const count = Math.min(input.readUInt16LE(eocd + 10), limit);
  let at = input.readUInt32LE(eocd + 16);
  if (at === 0xffffffff) return names;
  for (let index = 0; index < count; index += 1) {
    if (at + 46 > input.length || input.readUInt32LE(at) !== 0x02014b50) break;
    const nameLength = input.readUInt16LE(at + 28);
    names.push(input.subarray(at + 46, at + 46 + nameLength).toString("utf8"));
    at += 46 + nameLength + input.readUInt16LE(at + 30) + input.readUInt16LE(at + 32);
  }
  return names;
}

function expandZip(input: Buffer, limits: Limits): Expansion {
  const members: Member[] = [];
  const problems: string[] = [];
  const eocd = endOfCentralDirectory(input);
  if (eocd < 0) return { kind: "zip", members, problems: ["no zip end of central directory record"] };
  const count = input.readUInt16LE(eocd + 10);
  let at = input.readUInt32LE(eocd + 16);
  if (at === 0xffffffff) return { kind: "zip", members, problems: ["zip64 central directory, no reader"] };
  let total = 0;
  for (let index = 0; index < count; index += 1) {
    if (at + 46 > input.length || input.readUInt32LE(at) !== 0x02014b50) {
      problems.push(`zip central directory entry ${index} is not where the record says`);
      break;
    }
    const method = input.readUInt16LE(at + 10);
    const compressed = input.readUInt32LE(at + 20);
    const uncompressed = input.readUInt32LE(at + 24);
    const nameLength = input.readUInt16LE(at + 28);
    const extraLength = input.readUInt16LE(at + 30);
    const commentLength = input.readUInt16LE(at + 32);
    const localAt = input.readUInt32LE(at + 42);
    const name = input.subarray(at + 46, at + 46 + nameLength).toString("utf8");
    at += 46 + nameLength + extraLength + commentLength;
    if (name.endsWith("/")) continue;
    if (compressed === 0xffffffff || uncompressed === 0xffffffff || localAt === 0xffffffff) {
      problems.push(`zip member ${name} uses zip64 fields, no reader`);
      continue;
    }
    if (members.length >= limits.maxMembers) {
      problems.push(`zip holds more than ${limits.maxMembers} members; the rest were not read`);
      break;
    }
    if (uncompressed > limits.maxMemberBytes) {
      problems.push(`zip member ${name} is ${uncompressed} bytes, over the ${limits.maxMemberBytes} byte member limit`);
      continue;
    }
    if (localAt + 30 > input.length || input.readUInt32LE(localAt) !== 0x04034b50) {
      problems.push(`zip member ${name} has no local header at the recorded offset`);
      continue;
    }
    const dataAt = localAt + 30 + input.readUInt16LE(localAt + 26) + input.readUInt16LE(localAt + 28);
    const raw = input.subarray(dataAt, dataAt + compressed);
    if (raw.length !== compressed) {
      problems.push(`zip member ${name} is truncated`);
      continue;
    }
    let bytes: Buffer;
    try {
      if (method === 0) bytes = Buffer.from(raw);
      else if (method === 8) bytes = zlib.inflateRawSync(raw, { maxOutputLength: limits.maxMemberBytes });
      else {
        problems.push(`zip member ${name} uses compression method ${method}, no reader`);
        continue;
      }
    } catch (error) {
      problems.push(`zip member ${name} did not expand: ${(error as Error).message}`);
      continue;
    }
    total += bytes.length;
    if (total > limits.maxTotalBytes) {
      problems.push(`zip expands past the ${limits.maxTotalBytes} byte total limit at member ${name}`);
      break;
    }
    members.push({ path: name, bytes, sha256: digest(bytes) });
  }
  return { kind: "zip", members, problems };
}

/** Expand a container into its members. The caller has already classified the
 * bytes as a container; anything else throws, because guessing at a format is
 * how a layer stops being reproducible. */
export function expandContainer(input: Buffer, limits: Limits = defaultLimits): Expansion {
  if (input.length >= 2 && input[0] === 0x1f && input[1] === 0x8b) return expandGzip(input, limits);
  if (input.length >= 4 && input.subarray(0, 2).toString("latin1") === "PK") return expandZip(input, limits);
  if (input.length >= 512 && input.subarray(257, 262).toString("latin1") === "ustar") return expandTar(input, limits);
  throw new Error("expandContainer was given bytes that are not gzip, zip or tar");
}
