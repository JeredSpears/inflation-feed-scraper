import fetchProductData from "./fetchProductData.js";

/**
 * @param {object} config - retailer config from config.json
 * @param {string} config.storeId
 * @param {string} config.context
 * @param {Array<{productId: string, name: string}>} config.products
 * @returns {Promise<object[]>} flat price records
 */
export async function scrape({ storeId, context, products }) {
  const records = [];

  for (const { productId, name } of products) {
    const result = await fetchProductData(productId, storeId, context, { flatten: true });

    if (!result.success) {
      console.error(`  [heb] Failed for product ${productId}: ${result.error}`);
      continue;
    }

    const f = result.flattened;
    records.push({
      retailer: "heb",
      productId: f.productId,
      name: f.name ?? name,
      brand: f.brand ?? null,
      listPrice: f.listPrice ?? null,
      unit: f.unit ?? null,
      unitListPrice: f.unitListPrice ?? null,
      isOnSale: f.isOnSale ?? false,
      salePrice: f.salePrice ?? null,
      availability: f.availability ?? null,
    });
  }

  return records;
}
