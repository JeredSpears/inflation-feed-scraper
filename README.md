# inflation-feed-scraper
A scraper to grab pricing information from various retailers for specific products



```Graphql
inflation-feed-scraper/
├── scraper.js              ← main runner
├── config.json             ← groups of products to track by retailer
├── data/
│   ├── heb/
│   │   ├── product_export_<date>.json         ← flat output written each run
│   ├── kroger/
│       ├── product_export_<date>.json
└── retailers/
    ├── heb/
    │   ├── index.js        ← exports a scrape() function (used by main)
    │   └── fetchProductData.js
    ├── kroger/
    │   └── index.js
    └── walmart/
        └── index.js
```