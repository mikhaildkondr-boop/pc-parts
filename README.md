# PickMyPC - Custom PC Builder & SQLite Backend with Multi-Country Real Market Pricing

A modern PC Part Picker clone with an integrated **SQLite3** database, multi-country real market pricing, and REST API backend.

---

## 🌍 Supported Countries & Real Market Pricing

PickMyPC features dynamic localized pricing and authentic hardware retailers across major international markets:

| Flag & Country | Currency | New Retailers | Used / Secondary Marketplaces |
| :--- | :--- | :--- | :--- |
| 🇺🇦 **Ukraine** (`UA`) | **UAH (₴)** | Telemart, Rozetka, Brain, ITbox, Comfy | **OLX.ua, Overclockers.ua Барахолка, Telemart Outlet (Б/В), Rozetka Б/В** |
| 🇮🇹 **Italy** (`IT`) | **EUR (€)** | Amazon.it, Drako.it, BPM-Power, ePRICE | **Subito.it, eBay.it Usato, Amazon Seconda Mano (Warehouse), Vinted Tech** |
| 🇺🇸 **United States** (`US`) | **USD ($)** | Amazon, Newegg, Best Buy, Micro Center | **eBay Pre-Owned, r/hardwareswap, Jawa.gg, Micro Center Open Box** |
| 🇩🇪 **Germany** (`DE`) | **EUR (€)** | Mindfactory, Caseking, Alternate.de | **Kleinanzeigen Gebraucht, ComputerBase Marktplatz, Alternate Outlet** |
| 🇬🇧 **United Kingdom** (`GB`) | **GBP (£)** | Overclockers UK, Scan, Amazon UK | **eBay UK Used, CeX (webuy.com), Overclockers B-Grade, Gumtree** |
| 🇫🇷 **France** (`FR`) | **EUR (€)** | LDLC, TopAchat, Amazon.fr | **Leboncoin Occasion, LDLC Coin des Affaires, eBay.fr Occasion** |
| 🇪🇸 **Spain** (`ES`) | **EUR (€)** | PcComponentes, Coolmod, Amazon.es | **Wallapop Segunda Mano, PcComponentes Reacondicionados, Milanuncios** |
| 🇪🇺 **Europe (Pan-EU)** (`EU`) | **EUR (€)** | Caseking EU, Amazon EU, Computer Universe | **eBay Europe Refurbished, Caseking B-Ware, Refurbed.com** |

> 🚫 **Strict Exclusion**: Russia is completely excluded from the application, database, and API.

---

## ♻️ Used & Refurbished Hardware Features
- **Instant Condition Toggling**: Each selected component row can be toggled between Brand New and Pre-Owned with one click.
- **Used Savings Tracker**: Real-time counter showing exact money and percentage saved (e.g. Save $240 / 32%) vs brand new retail.
- **Condition Filter in Picker Modal**: Filter parts by `All Deals`, `✨ Brand New Only`, or `♻️ Used Only`.
- **Pre-Owned Preset Build**: `Used Market Value King (~$390 / ~16 500 ₴)` build featuring Ryzen 3600 + GTX 1660 Super on the secondary market.

---

## 🗄️ Database (SQLite)

The local database file is located at:
`pcparts.db`

### Schema Overview

1. **`parts` Table**:
   - `id` (TEXT, Primary Key) - e.g. `cpu-7800x3d`
   - `category` (TEXT) - `cpu`, `cooler`, `motherboard`, `memory`, `storage`, `gpu`, `case`, `psu`, `os`, `monitor`
   - `name` (TEXT) - Full product title
   - `brand` (TEXT) - AMD, Intel, NVIDIA, Corsair, etc.
   - `price` (REAL) - Base price in USD
   - `merchant` (TEXT) - Default retailer
   - `rating` (REAL) - Star rating (e.g. 4.9)
   - `reviews` (INTEGER) - Review count
   - `specs` (TEXT) - JSON payload with socket, TDP, form-factor, clock speeds
   - `created_at` (TIMESTAMP)

2. **`country_prices` Table**:
   - `part_id` (TEXT, Foreign Key -> `parts.id`)
   - `country_code` (TEXT) - `UA`, `IT`, `US`, `DE`, `GB`, `FR`, `ES`, `EU`
   - `currency` (TEXT) - `UAH`, `EUR`, `USD`, `GBP`
   - `price` (REAL) - Local brand new retail price
   - `merchant` (TEXT) - Local retailer
   - `shipping_info` (TEXT) - Local shipping info
   - `used_price` (REAL) - Local pre-owned / refurbished price (~25-42% discount)
   - `used_merchant` (TEXT) - Local secondary marketplace (e.g. OLX.ua, Subito.it, eBay, Kleinanzeigen)
   - `used_shipping_info` (TEXT) - Buyer protection & used shipping info
   - `used_savings` (REAL) - Monetary savings vs new
   - `used_savings_pct` (INTEGER) - Percentage saved vs new
   - `PRIMARY KEY (part_id, country_code)`

3. **`builds` Table**:
   - `id` (TEXT, Primary Key) - e.g. `build-sweet-spot-1440p`
   - `title` (TEXT) - Name of the build
   - `description` (TEXT) - Build description / notes
   - `total_price` (REAL) - Total calculated cost
   - `estimated_wattage` (INTEGER) - Estimated power draw in Watts
   - `parts_data` (TEXT) - JSON map of selected components
   - `created_at` (TIMESTAMP)

---

## 🛠️ Inspecting SQLite Directly from the Terminal

```powershell
# View all tables
sqlite3 pcparts.db ".tables"

# View parts summary by category
sqlite3 pcparts.db "SELECT category, count(*) FROM parts GROUP BY category;"

# View price comparison across countries for a specific CPU
sqlite3 pcparts.db "SELECT p.name, cp.country_code, cp.price, cp.currency, cp.merchant FROM parts p JOIN country_prices cp ON p.id = cp.part_id WHERE p.id = 'cpu-7800x3d';"

# View total localized prices count per country
sqlite3 pcparts.db "SELECT country_code, count(*) FROM country_prices GROUP BY country_code;"

# Open interactive SQLite shell
sqlite3 pcparts.db
```

To re-seed or synchronize the database at any time:
```powershell
python expand_full_hardware.py
```

---

## 🚀 Running the Backend REST API

To start the backend server whenever you want:

```powershell
python server.py
```

### Available Endpoints:
- `GET /api/status` - System health, SQLite version, and count of parts & builds
- `GET /api/countries` - List of all supported countries, currencies, and local retailers
- `GET /api/categories` - List of categories with parts counts
- `GET /api/parts` - List parts with optional country localization:
  - `?country=UA` (Ukraine - UAH prices & Telemart/Rozetka merchants)
  - `?country=IT` (Italy - EUR prices & Drako/Amazon.it merchants)
  - `?country=DE` (Germany - EUR prices & Mindfactory/Caseking merchants)
  - `?category=gpu&maxPrice=1000`
  - `?brand=AMD&search=ryzen`
- `GET /api/parts/<id>?country=IT` - Get individual part details with localized price and full country breakdown
- `POST /api/parts` - Add new component to SQLite
- `GET /api/builds` - Retrieve all saved community / user builds
- `GET /api/builds/<id>` - Retrieve specific build by ID
- `POST /api/builds` - Save a new configuration to SQLite
- `DELETE /api/builds/<id>` - Delete a saved build

---

## 🎮 Real-World Gaming Performance & FPS Simulator

The application features a physics-accurate gaming performance engine (`gaming_benchmarks.js`):
- **Dynamic Simulation**: Accurately computes expected real-world FPS based on the chosen CPU, GPU, and RAM capacity.
- **8 Iconic Benchmarks**: Counter-Strike 2, Cyberpunk 2077: Phantom Liberty, Black Myth: Wukong, Call of Duty: Warzone / BO6, Grand Theft Auto V, Elden Ring (60 FPS cap), Baldur's Gate 3 (Act 3 City draw-calls), and Fortnite.
- **Resolution & Preset Scaling**: Real-time switching between **1080p (FHD)**, **1440p (QHD)**, and **4K (UHD)**, as well as **Ultra / High** vs **Competitive / Esports** settings.
- **System Tier & Bottleneck Health**: Detects CPU bottlenecks vs GPU-bound pipelines, displays 1% Low stability ratings, and recommends target monitor refresh rates (60Hz, 144Hz, 240Hz+).
- **Responsive Gauge Bars**: Visual progress meters with 60 FPS and 144 FPS standard threshold markers.
