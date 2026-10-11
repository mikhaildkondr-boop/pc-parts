"""
Update Presets Script
Expands the graphics preset configurations across data.js, index.html, and SQLite pcparts.db.
Target Presets:
1. budget_1080p: Entry 1080p Gaming (~$550) - 1080p 60-100 FPS
2. used_budget: Used Market Value King (~$390) - 1080p Esports
3. esports_1080p: Competitive 240Hz Esports (~$920) - 1080p 240+ FPS
4. midrange: Sweet Spot 1440p High FPS (~$1,450) - 1440p 144+ FPS Ultra
5. amd_pure_1440p: All-AMD Raw Power 20GB (~$1,650) - 1440p/4K Native
6. raytracing_1440p: Ray Tracing & DLSS 3.5 Beast (~$2,050) - 1440p Path Tracing
7. enthusiast: Ultimate 4K 144Hz Enthusiast (~$2,850) - 4K 120+ FPS Ultra
8. titan_4k: The God Tier 4K Path-Tracing Titan (~$4,150) - 4K Max Everything
9. sff_mini_itx: Compact SFF Console Killer (~$1,520) - Mini-ITX Living Room
10. creator_workstation: Unreal Engine 5 & 3D 4K Workstation (~$3,350) - 3D/UE5
"""

import sqlite3
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_JS_FILE = os.path.join(BASE_DIR, "data.js")
DB_FILE = os.path.join(BASE_DIR, "pcparts.db")

PRESET_CONFIGS = {
    "budget_1080p": {
        "name": "Entry 1080p Gaming (~$550)",
        "badge": "1080p Value",
        "target": "1080p Medium/High • 60-100 FPS (CS2, Fortnite, GTA V)",
        "resolution": "1080p",
        "fps": "85 FPS",
        "desc": "AMD Ryzen 5 5500, Radeon RX 6600 8GB, 16GB DDR4, 1TB NVMe, 600W Bronze PSU.",
        "parts": {
            "cpu": "cpu-5500",
            "cooler": "cooler-assassin-x120",
            "motherboard": "mobo-b450-tomahawk-max",
            "memory": "ram-ripjaws-v-16-ddr4",
            "storage": "ssd-kingston-nv2-1tb",
            "gpu": "gpu-rx6600",
            "case": "case-fractal-pop",
            "psu": "psu-evga-600br"
        }
    },
    "used_budget": {
        "name": "Used Hardware Value King (~$390)",
        "badge": "♻️ Secondary Market",
        "target": "1080p Competitive • 90+ FPS on a tight budget",
        "resolution": "1080p",
        "fps": "95 FPS",
        "desc": "AMD Ryzen 5 3600, GTX 1660 Super 6GB (Pre-Owned Deal), 16GB DDR4, B450 Mobo.",
        "parts": {
            "cpu": "cpu-3600",
            "cooler": "cooler-pa120",
            "motherboard": "mobo-b450-tomahawk-max",
            "memory": "ram-ripjaws-v-16-ddr4",
            "storage": "ssd-crucial-p3plus-1tb",
            "gpu": "gpu-gtx1660super",
            "case": "case-h5-flow",
            "psu": "psu-corsair-cx650m"
        }
    },
    "esports_1080p": {
        "name": "Competitive 240Hz Esports (~$920)",
        "badge": "240Hz Esports",
        "target": "1080p Competitive • 240+ FPS (Valorant, Apex, CS2, Overwatch)",
        "resolution": "1080p",
        "fps": "240+ FPS",
        "desc": "AMD Ryzen 5 7600X, Radeon RX 7600 XT 16GB, 32GB DDR5-6000, 1TB NVMe Gen4, 650W Gold.",
        "parts": {
            "cpu": "cpu-7600x",
            "cooler": "cooler-pa120",
            "motherboard": "mobo-b650m-pro-rs",
            "memory": "ram-flare-x5-32-ddr5",
            "storage": "ssd-wd-sn770-1tb",
            "gpu": "gpu-rx7600xt",
            "case": "case-h5-flow",
            "psu": "psu-focus-650"
        }
    },
    "midrange": {
        "name": "Sweet Spot 1440p High FPS (~$1,450)",
        "badge": "⭐ Most Popular",
        "target": "1440p Ultra • 120-160 FPS (Cyberpunk, Wukong, Helldivers 2)",
        "resolution": "1440p",
        "fps": "135 FPS",
        "desc": "AMD Ryzen 5 7600X, GeForce RTX 4070 SUPER 12GB, 32GB DDR5-6000, 1TB SN850X, 750W Gold ATX 3.0.",
        "parts": {
            "cpu": "cpu-7600x",
            "cooler": "cooler-ps120se",
            "motherboard": "mobo-b650-tomahawk",
            "memory": "ram-flare-x5-32-ddr5",
            "storage": "ssd-wd-sn850x-1tb",
            "gpu": "gpu-rtx4070super",
            "case": "case-4000d",
            "psu": "psu-rm750e"
        }
    },
    "amd_pure_1440p": {
        "name": "All-AMD Raw Power 20GB (~$1,650)",
        "badge": "20GB VRAM Beast",
        "target": "1440p/4K Native Raster • 130+ FPS with massive VRAM buffer",
        "resolution": "1440p / 4K",
        "fps": "140 FPS",
        "desc": "AMD Ryzen 7 7700X, Radeon RX 7900 XT 20GB, 32GB DDR5-6000, 2TB Crucial T500, 850W Gold.",
        "parts": {
            "cpu": "cpu-7700x",
            "cooler": "cooler-ps120se",
            "motherboard": "mobo-b650-aorus-elite",
            "memory": "ram-vengeance-32-ddr5",
            "storage": "ssd-crucial-t500-2tb",
            "gpu": "gpu-rx7900xt",
            "case": "case-lancool-216",
            "psu": "psu-rm850e"
        }
    },
    "raytracing_1440p": {
        "name": "Ray Tracing & DLSS 3.5 Beast (~$2,050)",
        "badge": "Ray Tracing King",
        "target": "1440p Path Tracing • DLSS 3.5 Frame Gen • 120+ FPS",
        "resolution": "1440p / 4K",
        "fps": "125 FPS",
        "desc": "Intel Core i7-14700K 20-Core, RTX 4070 Ti SUPER 16GB, 32GB DDR5-6400, 2TB 990 Pro, 850W Gold.",
        "parts": {
            "cpu": "cpu-14700k",
            "cooler": "cooler-arctic-lf3-360",
            "motherboard": "mobo-z790-aorus",
            "memory": "ram-trident-z5-rgb-32-ddr5",
            "storage": "ssd-samsung-990pro-2tb",
            "gpu": "gpu-rtx4070tisuper",
            "case": "case-montech-air903",
            "psu": "psu-rm850e"
        }
    },
    "enthusiast": {
        "name": "Ultimate 4K 144Hz Enthusiast (~$2,850)",
        "badge": "🔥 4K Enthusiast",
        "target": "4K Ultra Max • 100-144 FPS (Uncompromised 4K Gaming)",
        "resolution": "4K UHD",
        "fps": "115 FPS",
        "desc": "AMD Ryzen 7 7800X3D (Gaming King), RTX 4080 SUPER 16GB, 32GB DDR5-6000 CL30, 2TB 990 Pro, 850W Gold.",
        "parts": {
            "cpu": "cpu-7800x3d",
            "cooler": "cooler-kraken360",
            "motherboard": "mobo-b650-tomahawk",
            "memory": "ram-vengeance-32-ddr5",
            "storage": "ssd-samsung-990pro-2tb",
            "gpu": "gpu-rtx4080super",
            "case": "case-o11-dynamic-evo",
            "psu": "psu-purepower-850"
        }
    },
    "titan_4k": {
        "name": "The God Tier 4K Path-Tracing Titan (~$4,150)",
        "badge": "👑 Peak Titan",
        "target": "4K Native Path Tracing Ultra • 160+ FPS • 24GB VRAM",
        "resolution": "4K UHD",
        "fps": "165 FPS",
        "desc": "AMD Ryzen 7 9800X3D, RTX 4090 24GB, 64GB DDR5-6000, 2TB Gen5 NVMe + 4TB 990 Pro, 1300W Titanium.",
        "parts": {
            "cpu": "cpu-9800x3d",
            "cooler": "cooler-arctic-lf3-360",
            "motherboard": "mobo-x670e-hero",
            "memory": "ram-dominator-tit-64-ddr5",
            "storage": "ssd-crucial-t705-2tb",
            "gpu": "gpu-rtx4090",
            "case": "case-hyte-y70",
            "psu": "psu-darkpower-1300"
        }
    },
    "sff_mini_itx": {
        "name": "Compact SFF Console Killer (~$1,520)",
        "badge": "🎒 Mini-ITX SFF",
        "target": "1440p High FPS in an 18L ultra-compact backpack/desk chassis",
        "resolution": "1440p",
        "fps": "130 FPS",
        "desc": "AMD Ryzen 5 7600, RTX 4070 SUPER 12GB, B650I Mini-ITX, 32GB DDR5, 1TB NVMe, NR200P V2 SFF Case.",
        "parts": {
            "cpu": "cpu-7600",
            "cooler": "cooler-nhu12s",
            "motherboard": "mobo-b650i-lightning",
            "memory": "ram-flare-x5-32-ddr5",
            "storage": "ssd-wd-sn850x-1tb",
            "gpu": "gpu-rtx4070super",
            "case": "case-nr200p-v2",
            "psu": "psu-rm750e"
        }
    },
    "creator_workstation": {
        "name": "Unreal Engine 5 & 3D 4K Workstation (~$3,350)",
        "badge": "🎬 Creator Workstation",
        "target": "4K Video Editing, Blender 3D, Unreal Engine 5 Dev, DaVinci 8K",
        "resolution": "4K / 8K Dev",
        "fps": "120 FPS",
        "desc": "Intel Core i9-14900K 24-Core, RTX 4080 SUPER 16GB, 64GB DDR5-6400, 4TB 990 Pro, 1200W Gold, Walnut North.",
        "parts": {
            "cpu": "cpu-14900k",
            "cooler": "cooler-arctic-lf3-360",
            "motherboard": "mobo-z790-aorus",
            "memory": "ram-trident-z5-rgb-64-ddr5",
            "storage": "ssd-samsung-990pro-4tb",
            "gpu": "gpu-rtx4080super",
            "case": "case-fractal-north",
            "psu": "psu-vertex-gx1200"
        }
    }
}

def update_data_js():
    with open(DATA_JS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    new_preset_js = f"const PRESET_BUILDS = {json.dumps(PRESET_CONFIGS, indent=2)};"
    parts = content.split("const PRESET_BUILDS =")
    if len(parts) == 2:
        new_content = parts[0] + new_preset_js + "\n"
    else:
        new_content = content + "\n\n" + new_preset_js

    with open(DATA_JS_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated PRESET_BUILDS in data.js with 10 presets.")

def update_sqlite():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    for key, p in PRESET_CONFIGS.items():
        # Calculate base total price
        total_p = 0.0
        wattage = 150
        for cat, part_id in p["parts"].items():
            cur.execute("SELECT price, specs FROM parts WHERE id = ?", (part_id,))
            row = cur.fetchone()
            if row:
                total_p += float(row[0])
                try:
                    sp = json.loads(row[1])
                    if "tdp" in sp:
                        wattage += int(sp["tdp"])
                except Exception:
                    pass

        cur.execute("""
            INSERT OR REPLACE INTO builds (id, title, description, total_price, estimated_wattage, parts_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"preset-{key}",
            p["name"],
            p["desc"],
            round(total_p, 2),
            wattage,
            json.dumps(p["parts"])
        ))

    conn.commit()
    cur.execute("SELECT count(*) FROM builds")
    print(f"Stored presets into SQLite database. Total builds in SQLite: {cur.fetchone()[0]}")
    conn.close()

if __name__ == "__main__":
    update_data_js()
    update_sqlite()
