import { HEB_SESSION_COOKIE } from "../../env-config.js";
import { sendRequest } from "../../lib/http.js";

const GRAPHQL_URL = "https://www.heb.com/graphql";
const DEFAULT_HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
  "Accept-Language": "en-US,en;q=0.9",
  Connection: "close",
  Cookie: HEB_SESSION_COOKIE ?? "",
};

const PRODUCT_DETAIL_QUERY = `
  query GetProductDetail($id: ID!, $storeId: ID!, $shoppingContext: ShoppingContext!) {
    productDetail(id: $id, storeId: $storeId, shoppingContext: $shoppingContext) {
      __typename
      ... on Product {
        id
        displayName
        brand { name }
        productCategory { name }
        SKUs {
          id
          contextPrices {
            context
            isOnSale
            listPrice { unit formattedAmount }
            salePrice { formattedAmount }
            unitListPrice { unit formattedAmount }
          }
          productAvailability
        }
      }
    }
  }
`;

/**
 * Fetch product detail data from HEB GraphQL API.
 * @param {string|number} productId
 * @param {string|number} storeId Store ID (e.g. 790).
 * @param {string} context Shopping context (e.g. CURBSIDE_PICKUP, IN_STORE).
 * @param {object} [options] Optional overrides { headers, flatten:boolean }.
 * @returns {Promise<{success:boolean,data?:object,flattened?:object,error?:string,status?:number}>}
 */
export async function fetchProductData(
  productId,
  storeId,
  context,
  options = {}) {

  if (!productId || !storeId || !context) {
    throw new Error("Missing required parameters: productId, storeId, or context");
  }

  const result = await sendRequest({
    url: GRAPHQL_URL,
    method: "POST",
    body: {
      query: PRODUCT_DETAIL_QUERY,
      variables: {
        id: String(productId),
        storeId: String(storeId),
        shoppingContext: context
      }
    },
    headers: { ...DEFAULT_HEADERS, ...(options.headers || {}) },
  });

  if (!result.success) return result;

  //i hate this .data.data.data.data.data matroshka
  const detail = result.data?.data?.productDetail;
  if (!detail) {
    return {
      success: false,
      status: result.status,
      error: "No productDetail in response",
      data: result.data,
    };
  }

  let flattened;
  if (options.flatten && detail.__typename === "Product") {
    const sku = detail.SKUs?.[0];
    const price = sku?.contextPrices?.[0];
    flattened = {
      productId: detail.id,
      name: detail.displayName,
      brand: detail.brand?.name,
      category: detail.productCategory?.name,
      skuId: sku?.id,
      listPrice: price?.listPrice?.formattedAmount,
      unit: price?.unitListPrice?.unit,
      unitListPrice: price?.unitListPrice?.formattedAmount,
      isOnSale: price?.isOnSale,
      salePrice: price?.salePrice?.formattedAmount,
      availability: sku?.productAvailability,
    };
  }

  return {
    success: true,
    status: result.status,
    data: result.data,
    ...(flattened ? { flattened } : {})
  };
}

export default fetchProductData;
