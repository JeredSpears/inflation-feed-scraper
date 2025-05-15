import requests
import json
from datetime import datetime

GRAPHQL_URL = "https://www.heb.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "close",
    "Cookie": "visid_incap_2302070=1Gy2mR1nRzCI07ih/eZ8t1Kmy2cAAAAAQUIPAAAAAACAX6qRrFiwor3lL3/Q2h/s"
}

def fetch_category_products(category_id, store_id, limit=5):
    query = """
    query BrowseCategory($categoryId: String!, $storeId: Int!, $limit: Int!) {
      browseCategory(
        categoryId: $categoryId
        storeId: $storeId
        shoppingContext: CURBSIDE_PICKUP
        limit: $limit
      ) {
        records {
          id
          displayName
          brand {
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
            }
            productAvailability
          }
        }
        total
      }
    }
    """
    
    variables = {
        "categoryId": category_id,
        "storeId": store_id,
        "limit": limit
    }

    response = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query, "variables": variables})
    
    if response.status_code != 200:
        print(f"Error fetching category {category_id}: {response.status_code}")
        return None

    try:
        data = response.json()
        records = data.get("data", {}).get("browseCategory", {}).get("records", [])
        flat_products = []
        for record in records:
            for sku in record.get("SKUs", []):
                context_prices = sku.get("contextPrices", [])
                for price in context_prices:
                    if price.get("listPrice"):
                        flat_products.append({
                            "id": record.get("id"),
                            "skuId": sku.get("id"),
                            "displayName": record.get("displayName"),
                            "brand": (record.get("brand") or {}).get("name"),
                            "listPrice": price["listPrice"].get("formattedAmount"),
                            "isOnSale": price.get("isOnSale"),
                        })
                        break
        return flat_products
    except (KeyError, TypeError, ValueError) as e:
        print(f"Error parsing data for category {category_id}: {e}")
        print(f"Response: {response}")
        return None

def main():
    category_id = "490043"  # Adjust to your desired category
    store_id = 790  # Adjust to the specific store context
    products = fetch_category_products(category_id, store_id, limit=50)

    if products:
        with open("category_products.json", "w", encoding="utf-8") as f:
            json.dump(products, f, indent=2)
        print(f"Saved {len(products)} products to category_products.json")
    else:
        print("No products found.")

if __name__ == "__main__":
    main()