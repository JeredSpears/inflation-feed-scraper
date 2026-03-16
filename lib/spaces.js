import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { readFile } from "fs/promises";

function getClient() {
  const { DO_SPACES_KEY, DO_SPACES_SECRET, DO_SPACES_REGION, DO_SPACES_ENDPOINT } = process.env;

  if (!DO_SPACES_KEY || !DO_SPACES_SECRET || !DO_SPACES_ENDPOINT) {
    throw new Error("Missing DO Spaces environment variables (DO_SPACES_KEY, DO_SPACES_SECRET, DO_SPACES_ENDPOINT)");
  }

  return new S3Client({
    endpoint: DO_SPACES_ENDPOINT,
    region: DO_SPACES_REGION ?? "us-east-1",
    credentials: {
      accessKeyId: DO_SPACES_KEY,
      secretAccessKey: DO_SPACES_SECRET
    },
    forcePathStyle: false
  });
}

/**
 * Upload a local file to DO Spaces.
 * @param {string} localPath - Absolute path to the file on disk
 * @param {string} remoteKey - Key (path) within the bucket, e.g. "heb/product_export_2026-03-15.json"
 */
export async function uploadFile(localPath, remoteKey) {
  const bucket = process.env.DO_SPACES_BUCKET;
  if (!bucket) throw new Error("Missing DO_SPACES_BUCKET environment variable");

  const body = await readFile(localPath);
  const client = getClient();

  await client.send(new PutObjectCommand({
    Bucket: bucket,
    Key: remoteKey,
    Body: body,
    ContentType: "application/json",
    ACL: "private"
  }));
}
