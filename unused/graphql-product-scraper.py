import requests
import json
from datetime import datetime
import time

GRAPHQL_URL = "https://www.heb.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "close",
    "Cookie": "visid_incap_2302070=1Gy2mR1nRzCI07ih/eZ8t1Kmy2cAAAAAQUIPAAAAAACAX6qRrFiwor3lL3/Q2h/s"
}

def fetch_product_detail(product_id, store_id, shopping_context):
    query = """
    query GetProductDetail($id: ID!, $storeId: ID!, $shoppingContext: ShoppingContext!) {
        productDetail(
            id: $id
            storeId: $storeId
            shoppingContext: $shoppingContext
        ) {
            __typename
            ... on Product {
                id
                displayName
                brand { name }
                productCategory {
                    name
                }
                SKUs {
                    id
                    contextPrices {
                        context
                        isOnSale
                        listPrice {
                            unit
                            formattedAmount
                        }
                        salePrice {
                            formattedAmount
                        }
                        unitListPrice {
                            unit
                            formattedAmount
                        }
                    }
                    productAvailability
                }
            }
        }
    }
    """
    
    variables = {
        "id": product_id,
        "storeId": store_id,
        "shoppingContext": shopping_context
    }

    response = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query, "variables": variables})
    
    if response.status_code != 200:
        print(f"Error fetching product {product_id}: {response.status_code}")
        print(f"Response: {response.text}")
        return None

    try:
        data = response.json()
        product = data["data"]["productDetail"]
        if not product or product["__typename"] != "Product":
            print(f"Product not found or not a Product type for {product_id}")
            return None

        # flatten the first SKU/contextPrice for simplicity
        sku = product["SKUs"][0] if product.get("SKUs") else {}
        context_price = sku.get("contextPrices", [{}])[0] if sku else {}

        return {
            "productId": product.get("id"),
            "name": product.get("displayName"),
            "brand": (product.get("brand") or {}).get("name"),
            "category": (product.get("productCategory") or {}).get("name"),
            "skuId": sku.get("id"),
            "listPrice": (context_price.get("listPrice") or {}).get("formattedAmount"),
            "salePrice": (context_price.get("salePrice") or {}).get("formattedAmount"),
            "unitListPrice": (context_price.get("unitListPrice") or {}).get("formattedAmount"),
            "unit": (context_price.get("unit") or {}).get("unit"),
            "isOnSale": context_price.get("isOnSale"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except (KeyError, TypeError, IndexError) as e:
        print(f"Error extracting product data for {product_id}: {e}")
        print(f"Response: {response.text}")
        return None

def main():
    product_ids = [
        "126644", 
        "539214", 
        "539002",
        "149725",
        "903540",
        "6189537",
        "533893",
        "690986",
        "314135"
        ]
    store_id = "790"
    shopping_context = "CURBSIDE_PICKUP"

    print(f"Fetching product details for {len(product_ids)} products...")

    results = []
    for idx, product_id in enumerate(product_ids):
        print(f"Fetching productId: {product_id} ({idx + 1}/{len(product_ids)})")
        data = fetch_product_detail(product_id, store_id, shopping_context)
        if data:
            results.append(data)
        if idx < len(product_ids) - 1:
            time.sleep(5)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"product_export_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Exported {len(results)} products to {filename}")

if __name__ == "__main__":
    main()