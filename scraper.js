import "dotenv/config";
import { readFile, writeFile, mkdir } from "fs/promises";
import { fileURLToPath } from "url";
import path from "path";
import { uploadFile } from "./lib/spaces.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function dateSuffix() {
  return new Date().toISOString().slice(0, 10); // yyyy-mm-dd
}

async function writeRetailerExport(retailerName, records) {
  const dir = path.join(__dirname, "data", retailerName);
  await mkdir(dir, { recursive: true });

  const filename = `product_export_${dateSuffix()}.json`;
  const localPath = path.join(dir, filename);
  const remoteKey = `${retailerName}/${filename}`;

  await writeFile(localPath, JSON.stringify(records, null, 2));

  try {
    await uploadFile(localPath, remoteKey);
    console.log(`[${retailerName}] Uploaded to Spaces: ${remoteKey}`);
  } catch (err) {
    console.error(`[${retailerName}] Spaces upload failed: ${err.message}`);
  }

  return path.join("data", retailerName, filename);
}

async function main() {
  const config = JSON.parse(
    await readFile(path.join(__dirname, "config.json"), "utf-8")
  );

  const errors = [];

  for (const [retailerName, retailerConfig] of Object.entries(config)) {
    const modulePath = `./retailers/${retailerName}/index.js`;
    let retailer;

    try {
      retailer = await import(modulePath);
    } catch (err) {
      console.error(`[${retailerName}] Failed to load module: ${err.message}`);
      errors.push({ retailer: retailerName, error: err.message });
      continue;
    }

    if (typeof retailer.scrape !== "function") {
      console.error(`[${retailerName}] Module does not export a scrape() function`);
      errors.push({ retailer: retailerName, error: "Missing scrape() export" });
      continue;
    }

    console.log(`[${retailerName}] Scraping ${retailerConfig.products.length} product(s)...`);
    let records;
    try {
      records = await retailer.scrape(retailerConfig);
    } catch (err) {
      console.error(`[${retailerName}] scrape() threw: ${err.message}`);
      errors.push({ retailer: retailerName, error: err.message });
      continue;
    }

    const writtenPath = await writeRetailerExport(retailerName, records);
    console.log(`[${retailerName}] Wrote ${records.length} record(s) to ${writtenPath}`);
  }

  if (errors.length > 0) {
    console.error(`\n${errors.length} retailer(s) had errors.`);
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("Fatal:", err.message);
  process.exit(1);
});
