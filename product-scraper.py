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

def fetch_product_detail(product_id, store_id, shopping_context):
    query = """
    query GetProductDetail($id: ID!, $storeId: ID!, $shoppingContext: ShoppingContext!) {
      productDetail(id: $id, storeId: $storeId, shoppingContext: $shoppingContext) {
        productView {
            id
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

        return {
            "product_id": product["id"],
            "name": product["name"],
            "brand": product["brand"],
            "category": product["category"],
            "price": product["price"],
            "quantity": product["quantity"],
            "is_own_brand": product["isOwnBrand"],
            "is_on_sale": product["isOnSale"],
            "is_on_ad": product["isOnAd"],
            "is_unavailable": product["isUnavailable"],
            "variant": product["variant"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except (KeyError, TypeError) as e:
        print(f"Error extracting product data for {product_id}: {e}")
        print(f"Response: {response.text}")
        return None

def main():
    product_ids = ["126644", "539214"]
    store_id = "790"  # Example store ID, may need adjustment
    shopping_context = "CURBSIDE_PICKUP"  # Adjust as needed

    for product_id in product_ids:
        data = fetch_product_detail(product_id, store_id, shopping_context)
        print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()