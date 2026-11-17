/** The R2 path refuses to run without its four values. It has never been run
 * against a live endpoint, so what is checked here is the refusal and the
 * shape of the signature, not the transfer. */
import { expect, it } from "vitest";
import { readSettings, signRequest } from "../scripts/archive/upload";

const settings = {
  accountId: "account",
  accessKeyId: "key",
  secretAccessKey: "secret",
  bucket: "archive",
};

it("names every missing environment variable rather than failing while signing", () => {
  expect(() => readSettings({})).toThrow(/R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET/);
  expect(() => readSettings({ R2_ACCOUNT_ID: "a", R2_ACCESS_KEY_ID: "b", R2_SECRET_ACCESS_KEY: "c" })).toThrow(/R2_BUCKET/);
  expect(readSettings({ R2_ACCOUNT_ID: "a", R2_ACCESS_KEY_ID: "b", R2_SECRET_ACCESS_KEY: "c", R2_BUCKET: "d" })).toEqual({
    accountId: "a",
    accessKeyId: "b",
    secretAccessKey: "c",
    bucket: "d",
  });
});

it("signs the method it is about to send, at the bucket path, with the payload hash", () => {
  const at = new Date("2026-11-17T09:00:00Z");
  const put = signRequest(settings, "PUT", "abc.gz", Buffer.from("bytes"), at);
  const head = signRequest(settings, "HEAD", "abc.gz", Buffer.alloc(0), at);
  expect(put.url).toBe("https://account.r2.cloudflarestorage.com/archive/abc.gz");
  expect(put.headers["x-amz-date"]).toBe("20261117T090000Z");
  expect(put.headers.Authorization).toMatch(/^AWS4-HMAC-SHA256 Credential=key\/20261117\/auto\/s3\/aws4_request, /);
  expect(put.headers.Authorization).not.toBe(head.headers.Authorization);
});
