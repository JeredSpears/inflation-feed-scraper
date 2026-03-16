# inflation-feed-scraper

a nodejs scraper that collects product prices from grocery retailers on a nightly schedule, writes dated JSON exports, and uploads them to digitalocean spaces for later ingestion into a database.

---

## Architecture

```Graphql
inflation-feed-scraper/
├── scraper.js                               ← cron entrypoint, orchestrates all retailers
├── config.json                              ← products to track, keyed by retailer name
├── lib/
│   ├── http.js                              ← generic sendRequest() utility
│   └── spaces.js                            ← DO Spaces upload utility (uploadFile)
├── retailers/
│   └── <name>/
│       ├── index.js                         ← exports async scrape
│       └── fetchProductData.js              ← retailer-specific fetch/transform logic
├── data/
│   └── <retailer>/
│       └── product_export_<yyyy-mm-dd>.json
└── .github/
    └── workflows/
        └── deploy.yml                       ← scheduled scraper run (6 AM UTC daily + workflow_dispatch)
```

the runner loads all retailers from `config.json`, calls each retailer's `scrape()`, writes a dated JSON file locally, then uploads it to DO Spaces. a planned web app will expose an ETL endpoint to ingest those exports into a database.

each retailer module exports a single function:

```js
export async function scrape({ storeId, context, products }) {
  // products: [{ productId, name }]
  // returns: flat record[]
}
```

To add a new retailer: create `retailers/<name>/index.js` exporting `scrape()` and add an entry to `config.json`. The runner picks it up automatically.

---

### To do
- add more retailers (kroger, walmart, etc.)
- web app ETL endpoint to ingest Spaces exports into a database
