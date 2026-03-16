import json
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright

class ProductScraper:
    def __init__(self, product_ids):
        self.base_url = 'https://www.heb.com/'
        self.product_ids = product_ids
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Referer': 'https://www.heb.com/',
        }

    async def get_product_data(self, page, product_id):
        url = f"{self.base_url}product-detail/{product_id}"
        try:
            print(f"Requesting {url}")
            response = await page.goto(url)
            html = await page.content()
            if response.status != 200:
                print(f"Error fetching product {product_id}: Status {response.status}")
                return None

            # Save the HTML content to a file for debugging
            with open(f"debug_{product_id}.html", "w", encoding="utf-8") as f:
                f.write(html)

            name_selector = 'div[data-qe-id="productDetails"][aria-label="product purchase details"] h1.sc-1922f016-4.wOsFJ'
            price_selector = 'div[data-qe-id="productDetails"][aria-label="product purchase details"] span.sc-d84f764b-1.jwINuz'

            name = await page.locator(name_selector).text_content()
            price = await page.locator(price_selector).text_content()

            count = await page.locator(name_selector).count()
            print(f"Found {count} elements for name_selector") 

            count = await page.locator(price_selector).count()
            print(f"Found {count} elements for name_selector") 

            if not name or not price:
                print(f"Data missing for product {product_id}: Name - {name}, Price - {price}")
                return None

            return {
                'product_id': product_id,
                'name': name.strip(),
                'price': price.strip(),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
        return None

    async def scrape_products(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()

            # it found out that i'm not real :(
            cookies = [
                {
                    "name": "visid_incap_2302070",
                    "value": "ejXXJ4/rQsqf4TFpp4g27z9IJWgAAAAAQUIPAAAAAADAKDw2NoTtagoLJ+9tdQ3m",
                    "domain": ".heb.com",
                    "path": "/"
                },
                {
                    "name": "incap_ses_68_2302070",
                    "value": "vJ5lUWwex37Bxw3t+ZXxAD9IJWgAAAAAZGgDoAozKAWWP1g/W9/1bw==",
                    "domain": ".heb.com",
                    "path": "/"
                }
            ]
            await context.add_cookies(cookies)

            results = []
            for product_id in self.product_ids:
                page = await context.new_page()
                data = await self.get_product_data(page, product_id)
                await page.close()
                if data:
                    results.append(data)
                await asyncio.sleep(2)  # 2 second delay between requests

            await browser.close()
            return results

    async def save_to_json(self, data, filename='products.json'):
        if data:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Data saved to {filename}")
        else:
            print("No data to save")

async def main():
    product_ids = [539002, 539214, 126644]
    scraper = ProductScraper(product_ids)
    product_data = await scraper.scrape_products()
    await scraper.save_to_json(product_data)

if __name__ == "__main__":
    asyncio.run(main())