"""
Database Initialization Script for PickMyPC.
Initializes SQLite database (pcparts.db) and seeds initial hardware components and builds.
"""

import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "pcparts.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create Parts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parts (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        brand TEXT NOT NULL,
        price REAL NOT NULL,
        merchant TEXT NOT NULL,
        rating REAL DEFAULT 0.0,
        reviews INTEGER DEFAULT 0,
        specs TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create Builds table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS builds (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        total_price REAL NOT NULL,
        estimated_wattage INTEGER NOT NULL,
        parts_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Create Country Prices table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS country_prices (
        part_id TEXT NOT NULL,
        country_code TEXT NOT NULL,
        currency TEXT NOT NULL,
        price REAL NOT NULL,
        merchant TEXT NOT NULL,
        shipping_info TEXT,
        used_price REAL,
        used_merchant TEXT,
        used_shipping_info TEXT,
        used_savings REAL,
        used_savings_pct INTEGER,
        PRIMARY KEY (part_id, country_code),
        FOREIGN KEY (part_id) REFERENCES parts(id) ON DELETE CASCADE
    );
    """)

    # Indexing for fast search and category filtering
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_parts_category ON parts(category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_parts_price ON parts(price);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_country_prices_country ON country_prices(country_code);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_country_prices_price ON country_prices(country_code, price);")

    conn.commit()
    print("Database tables initialized successfully.")
    return conn

def seed_parts(conn):
    cursor = conn.cursor()

    # Check if parts already exist
    cursor.execute("SELECT COUNT(*) FROM parts;")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Database already contains {count} parts. Skipping seed.")
        return

    # Seed parts catalog
    parts_data = [
        # CPUs
        {
            "id": "cpu-7800x3d",
            "category": "cpu",
            "name": "AMD Ryzen 7 7800X3D",
            "brand": "AMD",
            "price": 439.00,
            "merchant": "Amazon",
            "rating": 4.9,
            "reviews": 1420,
            "specs": {
                "socket": "AM5",
                "cores": "8 Cores / 16 Threads",
                "speed": "4.2 GHz (5.0 GHz Boost)",
                "tdp": 120,
                "hasGpu": True,
                "col1": "8 Cores @ 5.0GHz",
                "col2": "120W TDP • AM5"
            }
        },
        {
            "id": "cpu-7600x",
            "category": "cpu",
            "name": "AMD Ryzen 5 7600X",
            "brand": "AMD",
            "price": 194.99,
            "merchant": "Newegg",
            "rating": 4.8,
            "reviews": 980,
            "specs": {
                "socket": "AM5",
                "cores": "6 Cores / 12 Threads",
                "speed": "4.7 GHz (5.3 GHz Boost)",
                "tdp": 105,
                "hasGpu": True,
                "col1": "6 Cores @ 5.3GHz",
                "col2": "105W TDP • AM5"
            }
        },
        {
            "id": "cpu-14700k",
            "category": "cpu",
            "name": "Intel Core i7-14700K",
            "brand": "Intel",
            "price": 389.99,
            "merchant": "Best Buy",
            "rating": 4.7,
            "reviews": 820,
            "specs": {
                "socket": "LGA1700",
                "cores": "20 Cores (8P + 12E)",
                "speed": "3.4 GHz (5.6 GHz Boost)",
                "tdp": 253,
                "hasGpu": True,
                "col1": "20 Cores @ 5.6GHz",
                "col2": "253W TDP • LGA1700"
            }
        },
        {
            "id": "cpu-13600k",
            "category": "cpu",
            "name": "Intel Core i5-13600K",
            "brand": "Intel",
            "price": 254.99,
            "merchant": "Amazon",
            "rating": 4.8,
            "reviews": 1105,
            "specs": {
                "socket": "LGA1700",
                "cores": "14 Cores (6P + 8E)",
                "speed": "3.5 GHz (5.1 GHz Boost)",
                "tdp": 181,
                "hasGpu": True,
                "col1": "14 Cores @ 5.1GHz",
                "col2": "181W TDP • LGA1700"
            }
        },
        {
            "id": "cpu-5600",
            "category": "cpu",
            "name": "AMD Ryzen 5 5600",
            "brand": "AMD",
            "price": 116.99,
            "merchant": "Amazon",
            "rating": 4.8,
            "reviews": 3200,
            "specs": {
                "socket": "AM4",
                "cores": "6 Cores / 12 Threads",
                "speed": "3.5 GHz (4.4 GHz Boost)",
                "tdp": 65,
                "hasGpu": False,
                "col1": "6 Cores @ 4.4GHz",
                "col2": "65W TDP • AM4"
            }
        },
        # Coolers
        {
            "id": "cooler-pa120",
            "category": "cooler",
            "name": "Thermalright Peerless Assassin 120 SE",
            "brand": "Thermalright",
            "price": 34.90,
            "merchant": "Amazon",
            "rating": 4.8,
            "reviews": 2150,
            "specs": {
                "type": "Air Cooler (Dual Tower)",
                "supportedSockets": ["AM4", "AM5", "LGA1700"],
                "tdpSupport": 250,
                "col1": "Dual Tower 120mm Fans",
                "col2": "AM4 / AM5 / LGA1700"
            }
        },
        {
            "id": "cooler-nhd15",
            "category": "cooler",
            "name": "Noctua NH-D15 chromax.black",
            "brand": "Noctua",
            "price": 119.95,
            "merchant": "Amazon",
            "rating": 4.9,
            "reviews": 3410,
            "specs": {
                "type": "Air Cooler",
                "supportedSockets": ["AM4", "AM5", "LGA1700"],
                "tdpSupport": 280,
                "col1": "Dual Tower 140mm Fans",
                "col2": "AM4 / AM5 / LGA1700"
            }
        },
        {
            "id": "cooler-kraken360",
            "category": "cooler",
            "name": "NZXT Kraken Elite 360 RGB",
            "brand": "NZXT",
            "price": 279.99,
            "merchant": "Best Buy",
            "rating": 4.7,
            "reviews": 640,
            "specs": {
                "type": "Liquid AIO 360mm",
                "supportedSockets": ["AM4", "AM5", "LGA1700"],
                "tdpSupport": 320,
                "col1": "360mm Radiator + LCD Display",
                "col2": "AM4 / AM5 / LGA1700"
            }
        },
        # Motherboards
        {
            "id": "mobo-b650-tomahawk",
            "category": "motherboard",
            "name": "MSI MAG B650 TOMAHAWK WIFI",
            "brand": "MSI",
            "price": 189.99,
            "merchant": "Newegg",
            "rating": 4.6,
            "reviews": 645,
            "specs": {
                "socket": "AM5",
                "formFactor": "ATX",
                "ramType": "DDR5",
                "ramSlots": 4,
                "wifi": True,
                "col1": "ATX • AM5 • PCIe 4.0",
                "col2": "DDR5 • WiFi 6E • 3x M.2"
            }
        },
        {
            "id": "mobo-z790-aorus",
            "category": "motherboard",
            "name": "Gigabyte Z790 AORUS ELITE AX",
            "brand": "Gigabyte",
            "price": 229.99,
            "merchant": "Amazon",
            "rating": 4.6,
            "reviews": 580,
            "specs": {
                "socket": "LGA1700",
                "formFactor": "ATX",
                "ramType": "DDR5",
                "ramSlots": 4,
                "wifi": True,
                "col1": "ATX • LGA1700 • PCIe 5.0",
                "col2": "DDR5 • WiFi 6E • 4x M.2"
            }
        },
        {
            "id": "mobo-b550-gaming",
            "category": "motherboard",
            "name": "MSI B550-A PRO",
            "brand": "MSI",
            "price": 99.99,
            "merchant": "Amazon",
            "rating": 4.7,
            "reviews": 1840,
            "specs": {
                "socket": "AM4",
                "formFactor": "ATX",
                "ramType": "DDR4",
                "ramSlots": 4,
                "wifi": False,
                "col1": "ATX • AM4 • PCIe 4.0",
                "col2": "DDR4 • 2x M.2"
            }
        },
        {
            "id": "mobo-b650i-lightning",
            "category": "motherboard",
            "name": "ASRock B650I Lightning WiFi",
            "brand": "ASRock",
            "price": 199.99,
            "merchant": "Newegg",
            "rating": 4.5,
            "reviews": 140,
            "specs": {
                "socket": "AM5",
                "formFactor": "Mini-ITX",
                "ramType": "DDR5",
                "ramSlots": 2,
                "wifi": True,
                "col1": "Mini-ITX • AM5",
                "col2": "DDR5 • WiFi 6E"
            }
        },
        # Memory
        {
            "id": "ram-vengeance-32-ddr5",
            "category": "memory",
            "name": "Corsair Vengeance 32 GB (2 x 16 GB) DDR5-6000 CL30",
            "brand": "Corsair",
            "price": 114.99,
            "merchant": "Amazon",
            "rating": 4.8,
            "reviews": 2310,
            "specs": {
                "type": "DDR5",
                "speed": "DDR5-6000",
                "capacity": "32 GB (2 x 16 GB)",
                "col1": "32 GB (2x16GB) • CL30",
                "col2": "DDR5-6000 • 1.35V"
            }
        },
        {
            "id": "ram-flare-x5-32-ddr5",
            "category": "memory",
            "name": "G.Skill Flare X5 32 GB (2 x 16 GB) DDR5-6000 CL32",
            "brand": "G.Skill",
            "price": 99.99,
            "merchant": "Newegg",
            "rating": 4.7,
            "reviews": 1450,
            "specs": {
                "type": "DDR5",
                "speed": "DDR5-6000",
                "capacity": "32 GB (2 x 16 GB)",
                "col1": "32 GB (2x16GB) • CL32",
                "col2": "DDR5-6000 • AMD EXPO"
            }
        },
        {
            "id": "ram-ripjaws-16-ddr4",
            "category": "memory",
            "name": "G.Skill Ripjaws V 16 GB (2 x 8 GB) DDR4-3200 CL16",
            "brand": "G.Skill",
            "price": 35.99,
            "merchant": "Amazon",
            "rating": 4.8,
            "reviews": 4200,
            "specs": {
                "type": "DDR4",
                "speed": "DDR4-3200",
                "capacity": "16 GB (2 x 8 GB)",
                "col1": "16 GB (2x8GB) • CL16",
                "col2": "DDR4-3200"
            }
        },
        # Storage
        {
            "id": "storage-990pro-2tb",
            "category": "storage",
            "name": "Samsung 990 Pro 2 TB M.2-2280 NVMe SSD",
            "brand": "Samsung",
            "price": 169.99,
            "merchant": "Amazon",
            "rating": 4.9,
            "reviews": 3200,
            "specs": {
                "capacity": "2 TB",
                "col1": "2 TB M.2 NVMe Gen4",
                "col2": "Up to 7,450 MB/s Read"
            }
        },
        {
            "id": "storage-sn850x-1tb",
            "category": "storage",
            "name": "Western Digital Black SN850X 1 TB M.2 NVMe",
            "brand": "Western Digital",
            "price": 94.99,
            "merchant": "Best Buy",
            "rating": 4.8,
            "reviews": 1890,
            "specs": {
                "capacity": "1 TB",
                "col1": "1 TB M.2 NVMe Gen4",
                "col2": "Up to 7,300 MB/s Read"
            }
        },
        {
            "id": "storage-crucial-p3-1tb",
            "category": "storage",
            "name": "Crucial P3 Plus 1 TB M.2 NVMe SSD",
            "brand": "Crucial",
            "price": 61.99,
            "merchant": "Amazon",
            "rating": 4.7,
            "reviews": 2150,
            "specs": {
                "capacity": "1 TB",
                "col1": "1 TB M.2 NVMe Gen4",
                "col2": "Up to 5,000 MB/s Read"
            }
        },
        # Video Cards
        {
            "id": "gpu-rtx4080super",
            "category": "gpu",
            "name": "Gigabyte WINDFORCE V2 GeForce RTX 4080 SUPER 16 GB",
            "brand": "NVIDIA / Gigabyte",
            "price": 999.99,
            "merchant": "Best Buy",
            "rating": 4.8,
            "reviews": 740,
            "specs": {
                "chipset": "GeForce RTX 4080 SUPER",
                "vram": "16 GB GDDR6X",
                "tdp": 320,
                "lengthMm": 330,
                "col1": "16 GB GDDR6X • 2550 MHz",
                "col2": "320W TDP • 330mm Length"
            }
        },
        {
            "id": "gpu-rtx4070super",
            "category": "gpu",
            "name": "ASUS DUAL OC GeForce RTX 4070 SUPER 12 GB",
            "brand": "NVIDIA / ASUS",
            "price": 599.99,
            "merchant": "Newegg",
            "rating": 4.8,
            "reviews": 950,
            "specs": {
                "chipset": "GeForce RTX 4070 SUPER",
                "vram": "12 GB GDDR6X",
                "tdp": 220,
                "lengthMm": 267,
                "col1": "12 GB GDDR6X • Dual Fan",
                "col2": "220W TDP • 267mm Length"
            }
        },
        {
            "id": "gpu-rx7800xt",
            "category": "gpu",
            "name": "Sapphire PULSE Radeon RX 7800 XT 16 GB",
            "brand": "AMD / Sapphire",
            "price": 489.99,
            "merchant": "Amazon",
            "rating": 4.7,
            "reviews": 1250,
            "specs": {
                "chipset": "Radeon RX 7800 XT",
                "vram": "16 GB GDDR6",
                "tdp": 263,
                "lengthMm": 280,
                "col1": "16 GB GDDR6 • Dual Fan",
                "col2": "263W TDP • 280mm Length"
            }
        },
        {
            "id": "gpu-rx6600",
            "category": "gpu",
            "name": "ASRock Challenger D Radeon RX 6600 8 GB",
            "brand": "AMD / ASRock",
            "price": 189.99,
            "merchant": "Newegg",
            "rating": 4.6,
            "reviews": 1980,
            "specs": {
                "chipset": "Radeon RX 6600",
                "vram": "8 GB GDDR6",
                "tdp": 132,
                "lengthMm": 269,
                "col1": "8 GB GDDR6 • Dual Fan",
                "col2": "132W TDP • 269mm Length"
            }
        },
        {
            "id": "gpu-rtx4090",
            "category": "gpu",
            "name": "MSI GAMING X SLIM GeForce RTX 4090 24 GB",
            "brand": "NVIDIA / MSI",
            "price": 1749.99,
            "merchant": "Amazon",
            "rating": 4.9,
            "reviews": 620,
            "specs": {
                "chipset": "GeForce RTX 4090",
                "vram": "24 GB GDDR6X",
                "tdp": 450,
                "lengthMm": 322,
                "col1": "24 GB GDDR6X • Triple Fan",
                "col2": "450W TDP • 322mm Length"
            }
        },
        # Cases
        {
            "id": "case-h5-flow",
            "category": "case",
            "name": "NZXT H5 Flow ATX Mid Tower Case",
            "brand": "NZXT",
            "price": 88.99,
            "merchant": "Amazon",
            "rating": 4.7,
            "reviews": 2150,
            "specs": {
                "formFactor": "ATX",
                "supportedMobos": ["ATX", "Micro-ATX", "Mini-ITX"],
                "sidePanel": "Tempered Glass",
                "maxGpuLengthMm": 365,
                "col1": "Mid Tower • Tempered Glass",
                "col2": "Up to 365mm GPU • High Airflow"
            }
        },
        {
            "id": "case-4000d",
            "category": "case",
            "name": "Corsair 4000D Airflow ATX Mid Tower Case",
            "brand": "Corsair",
            "price": 89.99,
            "merchant": "Best Buy",
            "rating": 4.8,
            "reviews": 4520,
            "specs": {
                "formFactor": "ATX",
                "supportedMobos": ["ATX", "Micro-ATX", "Mini-ITX"],
                "sidePanel": "Tempered Glass",
                "maxGpuLengthMm": 360,
                "col1": "Mid Tower • RapidRoute Routing",
                "col2": "Up to 360mm GPU • Airflow Front"
            }
        },
        # Power Supplies
        {
            "id": "psu-rm850e",
            "category": "psu",
            "name": "Corsair RM850e (2023) 850 W 80+ Gold Modular",
            "brand": "Corsair",
            "price": 119.99,
            "merchant": "Amazon",
            "rating": 4.8,
            "reviews": 1980,
            "specs": {
                "wattage": 850,
                "efficiency": "80+ Gold",
                "col1": "850 Watts • 80+ Gold",
                "col2": "ATX 3.0 & PCIe 5.0 Ready"
            }
        },
        {
            "id": "psu-rm750e",
            "category": "psu",
            "name": "Corsair RM750e (2023) 750 W 80+ Gold Modular",
            "brand": "Corsair",
            "price": 99.99,
            "merchant": "Best Buy",
            "rating": 4.7,
            "reviews": 1420,
            "specs": {
                "wattage": 750,
                "efficiency": "80+ Gold",
                "col1": "750 Watts • 80+ Gold",
                "col2": "Fully Modular • ATX 3.0"
            }
        },
        {
            "id": "psu-focus-650",
            "category": "psu",
            "name": "SeaSonic FOCUS GX 650 W 80+ Gold Fully Modular",
            "brand": "SeaSonic",
            "price": 89.99,
            "merchant": "Newegg",
            "rating": 4.8,
            "reviews": 950,
            "specs": {
                "wattage": 650,
                "efficiency": "80+ Gold",
                "col1": "650 Watts • 80+ Gold",
                "col2": "Fully Modular • 10 Yr Warranty"
            }
        },
        # OS & Monitors
        {
            "id": "os-win11-home",
            "category": "os",
            "name": "Microsoft Windows 11 Home - USB 64-bit",
            "brand": "Microsoft",
            "price": 119.99,
            "merchant": "Amazon",
            "rating": 4.6,
            "reviews": 3100,
            "specs": {
                "version": "Windows 11 Home",
                "col1": "Windows 11 Home",
                "col2": "Retail License (USB)"
            }
        },
        {
            "id": "monitor-m27q",
            "category": "monitor",
            "name": "Gigabyte M27Q 27.0\" 2560 x 1440 170 Hz IPS",
            "brand": "Gigabyte",
            "price": 249.99,
            "merchant": "Amazon",
            "rating": 4.7,
            "reviews": 2430,
            "specs": {
                "resolution": "2560 x 1440",
                "col1": "27.0\" • 2560 x 1440 • 170 Hz",
                "col2": "IPS • FreeSync Premium"
            }
        }
    ]

    for p in parts_data:
        cursor.execute("""
            INSERT OR REPLACE INTO parts (id, category, name, brand, price, merchant, rating, reviews, specs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["id"],
            p["category"],
            p["name"],
            p["brand"],
            p["price"],
            p["merchant"],
            p["rating"],
            p["reviews"],
            json.dumps(p["specs"])
        ))

    # Seed Sample Community Builds
    sample_builds = [
        {
            "id": "build-sweet-spot-1440p",
            "title": "Sweet Spot 1440p Gaming",
            "description": "Balanced high-FPS gaming rig with Ryzen 7600X and RTX 4070 Super.",
            "total_price": 1449.88,
            "estimated_wattage": 420,
            "parts_data": {
                "cpu": "cpu-7600x",
                "cooler": "cooler-pa120",
                "motherboard": "mobo-b650-tomahawk",
                "memory": "ram-flare-x5-32-ddr5",
                "storage": "storage-sn850x-1tb",
                "gpu": "gpu-rtx4070super",
                "case": "case-4000d",
                "psu": "psu-rm750e"
            }
        },
        {
            "id": "build-ultimate-4k",
            "title": "Ultimate 4K Enthusiast",
            "description": "Top-tier gaming build with Ryzen 7800X3D and RTX 4080 Super.",
            "total_price": 2869.80,
            "estimated_wattage": 520,
            "parts_data": {
                "cpu": "cpu-7800x3d",
                "cooler": "cooler-kraken360",
                "motherboard": "mobo-b650-tomahawk",
                "memory": "ram-vengeance-32-ddr5",
                "storage": "storage-990pro-2tb",
                "gpu": "gpu-rtx4080super",
                "case": "case-4000d",
                "psu": "psu-rm850e"
            }
        }
    ]

    for b in sample_builds:
        cursor.execute("""
            INSERT OR REPLACE INTO builds (id, title, description, total_price, estimated_wattage, parts_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            b["id"],
            b["title"],
            b["description"],
            b["total_price"],
            b["estimated_wattage"],
            json.dumps(b["parts_data"])
        ))

    conn.commit()
    print(f"Successfully seeded {len(parts_data)} parts and {len(sample_builds)} builds.")

if __name__ == "__main__":
    connection = init_db()
    seed_parts(connection)
    connection.close()
    print(f"SQLite database is ready at: {DB_FILE}")
