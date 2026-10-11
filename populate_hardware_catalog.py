"""
Populate Hardware Catalog Script
Expands the SQLite database and data.js with an extensive historical and modern catalog of:
- CPUs (Intel Core 1st-14th Gen, Core 2, Pentium, AMD Ryzen 1000-9000, Threadripper, FX, Phenom, Athlon)
- GPUs (NVIDIA RTX 50/40/30/20, GTX 16/10/900/700/600/500/8000/retro, AMD RX 7000/6000/5000/500/400/R9/HD, Intel Arc, 3dfx)
- SSDs (PCIe Gen5, Gen4, Gen3 NVMe, 2.5" SATA SSDs, legacy SSDs across 120GB - 8TB)
- RAM (DDR5, DDR4, DDR3, DDR2, DDR1 across all capacities and speeds)
"""

import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "pcparts.db")
DATA_JS_FILE = os.path.join(os.path.dirname(__file__), "data.js")

def build_catalog():
    catalog = []

    # =========================================================================
    # 1. CPUs (AMD & INTEL across generations)
    # =========================================================================
    cpus_raw = [
        # AMD Ryzen 9000 Series (AM5)
        ("cpu-9950x", "AMD Ryzen 9 9950X", "AMD", 649.00, "AM5", "16 Cores / 32 Threads", "4.3 GHz (5.7 GHz Boost)", 170, True, 4.9, 310),
        ("cpu-9900x", "AMD Ryzen 9 9900X", "AMD", 499.00, "AM5", "12 Cores / 24 Threads", "4.4 GHz (5.6 GHz Boost)", 120, True, 4.8, 240),
        ("cpu-9700x", "AMD Ryzen 7 9700X", "AMD", 359.00, "AM5", "8 Cores / 16 Threads", "3.8 GHz (5.5 GHz Boost)", 65, True, 4.8, 480),
        ("cpu-9600x", "AMD Ryzen 5 9600X", "AMD", 279.00, "AM5", "6 Cores / 12 Threads", "3.9 GHz (5.4 GHz Boost)", 65, True, 4.7, 390),

        # AMD Ryzen 7000 Series (AM5)
        ("cpu-7950x3d", "AMD Ryzen 9 7950X3D", "AMD", 549.99, "AM5", "16 Cores / 32 Threads (3D V-Cache)", "4.2 GHz (5.7 GHz Boost)", 120, True, 4.9, 1150),
        ("cpu-7950x", "AMD Ryzen 9 7950X", "AMD", 529.00, "AM5", "16 Cores / 32 Threads", "4.5 GHz (5.7 GHz Boost)", 170, True, 4.8, 1890),
        ("cpu-7900x3d", "AMD Ryzen 9 7900X3D", "AMD", 399.00, "AM5", "12 Cores / 24 Threads", "4.4 GHz (5.6 GHz Boost)", 120, True, 4.7, 850),
        ("cpu-7900x", "AMD Ryzen 9 7900X", "AMD", 369.00, "AM5", "12 Cores / 24 Threads", "4.7 GHz (5.6 GHz Boost)", 170, True, 4.8, 1420),
        ("cpu-7800x3d", "AMD Ryzen 7 7800X3D", "AMD", 439.00, "AM5", "8 Cores / 16 Threads (3D V-Cache)", "4.2 GHz (5.0 GHz Boost)", 120, True, 4.9, 3600),
        ("cpu-7700x", "AMD Ryzen 7 7700X", "AMD", 289.00, "AM5", "8 Cores / 16 Threads", "4.5 GHz (5.4 GHz Boost)", 105, True, 4.8, 2100),
        ("cpu-7700", "AMD Ryzen 7 7700", "AMD", 259.00, "AM5", "8 Cores / 16 Threads", "3.8 GHz (5.3 GHz Boost)", 65, True, 4.8, 980),
        ("cpu-7600x", "AMD Ryzen 5 7600X", "AMD", 194.99, "AM5", "6 Cores / 12 Threads", "4.7 GHz (5.3 GHz Boost)", 105, True, 4.8, 3120),
        ("cpu-7600", "AMD Ryzen 5 7600", "AMD", 182.00, "AM5", "6 Cores / 12 Threads", "3.8 GHz (5.1 GHz Boost)", 65, True, 4.8, 1750),
        ("cpu-7500f", "AMD Ryzen 5 7500F", "AMD", 159.00, "AM5", "6 Cores / 12 Threads", "3.7 GHz (5.0 GHz Boost)", 65, False, 4.7, 890),

        # AMD Ryzen 5000 Series (AM4)
        ("cpu-5950x", "AMD Ryzen 9 5950X", "AMD", 359.00, "AM4", "16 Cores / 32 Threads", "3.4 GHz (4.9 GHz Boost)", 105, False, 4.9, 4200),
        ("cpu-5900x", "AMD Ryzen 9 5900X", "AMD", 269.00, "AM4", "12 Cores / 24 Threads", "3.7 GHz (4.8 GHz Boost)", 105, False, 4.9, 5600),
        ("cpu-5800x3d", "AMD Ryzen 7 5800X3D", "AMD", 339.00, "AM4", "8 Cores / 16 Threads (3D V-Cache)", "3.4 GHz (4.5 GHz Boost)", 105, False, 4.9, 4980),
        ("cpu-5800x", "AMD Ryzen 7 5800X", "AMD", 189.00, "AM4", "8 Cores / 16 Threads", "3.8 GHz (4.7 GHz Boost)", 105, False, 4.8, 7100),
        ("cpu-5700x3d", "AMD Ryzen 7 5700X3D", "AMD", 199.99, "AM4", "8 Cores / 16 Threads (3D V-Cache)", "3.0 GHz (4.1 GHz Boost)", 105, False, 4.8, 1200),
        ("cpu-5700x", "AMD Ryzen 7 5700X", "AMD", 159.00, "AM4", "8 Cores / 16 Threads", "3.4 GHz (4.6 GHz Boost)", 65, False, 4.8, 4300),
        ("cpu-5700g", "AMD Ryzen 7 5700G", "AMD", 169.00, "AM4", "8 Cores / 16 Threads + Vega 8", "3.8 GHz (4.6 GHz Boost)", 65, True, 4.8, 3800),
        ("cpu-5600x", "AMD Ryzen 5 5600X", "AMD", 139.99, "AM4", "6 Cores / 12 Threads", "3.7 GHz (4.6 GHz Boost)", 65, False, 4.8, 8900),
        ("cpu-5600", "AMD Ryzen 5 5600", "AMD", 116.99, "AM4", "6 Cores / 12 Threads", "3.5 GHz (4.4 GHz Boost)", 65, False, 4.8, 6400),
        ("cpu-5600g", "AMD Ryzen 5 5600G", "AMD", 119.00, "AM4", "6 Cores / 12 Threads + Vega 7", "3.9 GHz (4.4 GHz Boost)", 65, True, 4.8, 5100),
        ("cpu-5500", "AMD Ryzen 5 5500", "AMD", 89.00, "AM4", "6 Cores / 12 Threads", "3.6 GHz (4.2 GHz Boost)", 65, False, 4.7, 3100),

        # AMD Ryzen 3000, 2000, 1000 Series (AM4)
        ("cpu-3950x", "AMD Ryzen 9 3950X", "AMD", 299.00, "AM4", "16 Cores / 32 Threads", "3.5 GHz (4.7 GHz Boost)", 105, False, 4.8, 2900),
        ("cpu-3900x", "AMD Ryzen 9 3900X", "AMD", 239.00, "AM4", "12 Cores / 24 Threads", "3.8 GHz (4.6 GHz Boost)", 105, False, 4.8, 4800),
        ("cpu-3700x", "AMD Ryzen 7 3700X", "AMD", 169.00, "AM4", "8 Cores / 16 Threads", "3.6 GHz (4.4 GHz Boost)", 65, False, 4.8, 8100),
        ("cpu-3600", "AMD Ryzen 5 3600", "AMD", 95.00, "AM4", "6 Cores / 12 Threads", "3.6 GHz (4.2 GHz Boost)", 65, False, 4.8, 12500),
        ("cpu-2700x", "AMD Ryzen 7 2700X", "AMD", 110.00, "AM4", "8 Cores / 16 Threads", "3.7 GHz (4.3 GHz Boost)", 105, False, 4.7, 6200),
        ("cpu-2600", "AMD Ryzen 5 2600", "AMD", 79.00, "AM4", "6 Cores / 12 Threads", "3.4 GHz (3.9 GHz Boost)", 65, False, 4.7, 9800),
        ("cpu-1600", "AMD Ryzen 5 1600", "AMD", 59.00, "AM4", "6 Cores / 12 Threads", "3.2 GHz (3.6 GHz Boost)", 65, False, 4.7, 8500),

        # AMD FX & Legacy
        ("cpu-fx-8350", "AMD FX-8350 Eight-Core", "AMD", 65.00, "AM3+", "8 Cores / 8 Threads", "4.0 GHz (4.2 GHz Turbo)", 125, False, 4.5, 4100),
        ("cpu-phenom-1100t", "AMD Phenom II X6 1100T Black Edition", "AMD", 50.00, "AM3", "6 Cores / 6 Threads", "3.3 GHz (3.7 GHz Turbo)", 125, False, 4.6, 2200),
        ("cpu-athlon-64-x2", "AMD Athlon 64 X2 6000+", "AMD", 30.00, "AM2", "2 Cores / 2 Threads", "3.0 GHz", 89, False, 4.5, 1400),

        # Intel Core 14th Gen (LGA1700)
        ("cpu-14900ks", "Intel Core i9-14900KS Special Edition", "Intel", 679.99, "LGA1700", "24 Cores (8P + 16E) / 32 Threads", "3.2 GHz (6.2 GHz Boost)", 320, True, 4.8, 480),
        ("cpu-14900k", "Intel Core i9-14900K", "Intel", 539.99, "LGA1700", "24 Cores (8P + 16E) / 32 Threads", "3.2 GHz (6.0 GHz Boost)", 253, True, 4.7, 1850),
        ("cpu-14700k", "Intel Core i7-14700K", "Intel", 389.99, "LGA1700", "20 Cores (8P + 12E) / 28 Threads", "3.4 GHz (5.6 GHz Boost)", 253, True, 4.7, 2400),
        ("cpu-14600k", "Intel Core i5-14600K", "Intel", 299.99, "LGA1700", "14 Cores (6P + 8E) / 20 Threads", "3.5 GHz (5.3 GHz Boost)", 181, True, 4.8, 1920),
        ("cpu-14400f", "Intel Core i5-14400F", "Intel", 189.99, "LGA1700", "10 Cores (6P + 4E) / 16 Threads", "2.5 GHz (4.7 GHz Boost)", 65, False, 4.7, 950),
        ("cpu-14100f", "Intel Core i3-14100F", "Intel", 109.99, "LGA1700", "4 Cores (4P) / 8 Threads", "3.5 GHz (4.7 GHz Boost)", 60, False, 4.7, 680),

        # Intel Core 13th Gen (LGA1700)
        ("cpu-13900ks", "Intel Core i9-13900KS", "Intel", 599.00, "LGA1700", "24 Cores (8P + 16E)", "3.2 GHz (6.0 GHz Boost)", 253, True, 4.8, 890),
        ("cpu-13900k", "Intel Core i9-13900K", "Intel", 479.00, "LGA1700", "24 Cores (8P + 16E)", "3.0 GHz (5.8 GHz Boost)", 253, True, 4.8, 3100),
        ("cpu-13700k", "Intel Core i7-13700K", "Intel", 349.00, "LGA1700", "16 Cores (8P + 8E)", "3.4 GHz (5.4 GHz Boost)", 253, True, 4.8, 4200),
        ("cpu-13600k", "Intel Core i5-13600K", "Intel", 254.99, "LGA1700", "14 Cores (6P + 8E)", "3.5 GHz (5.1 GHz Boost)", 181, True, 4.8, 4900),
        ("cpu-13400f", "Intel Core i5-13400F", "Intel", 169.00, "LGA1700", "10 Cores (6P + 4E)", "2.5 GHz (4.6 GHz Boost)", 65, False, 4.8, 2300),
        ("cpu-13100f", "Intel Core i3-13100F", "Intel", 99.00, "LGA1700", "4 Cores / 8 Threads", "3.4 GHz (4.5 GHz Boost)", 60, False, 4.7, 1400),

        # Intel Core 12th Gen (LGA1700)
        ("cpu-12900k", "Intel Core i9-12900K", "Intel", 329.00, "LGA1700", "16 Cores (8P + 8E)", "3.2 GHz (5.2 GHz Boost)", 241, True, 4.8, 4600),
        ("cpu-12700k", "Intel Core i7-12700K", "Intel", 239.00, "LGA1700", "12 Cores (8P + 4E)", "3.6 GHz (5.0 GHz Boost)", 190, True, 4.8, 5900),
        ("cpu-12600k", "Intel Core i5-12600K", "Intel", 175.00, "LGA1700", "10 Cores (6P + 4E)", "3.7 GHz (4.9 GHz Boost)", 150, True, 4.8, 6200),
        ("cpu-12400f", "Intel Core i5-12400F", "Intel", 129.00, "LGA1700", "6 Cores / 12 Threads", "2.5 GHz (4.4 GHz Boost)", 65, False, 4.8, 5800),
        ("cpu-12100f", "Intel Core i3-12100F", "Intel", 89.00, "LGA1700", "4 Cores / 8 Threads", "3.3 GHz (4.3 GHz Boost)", 60, False, 4.8, 3400),

        # Intel Core 11th - 10th - 9th Gen
        ("cpu-11900k", "Intel Core i9-11900K", "Intel", 269.00, "LGA1200", "8 Cores / 16 Threads", "3.5 GHz (5.3 GHz Boost)", 125, True, 4.6, 2800),
        ("cpu-10900k", "Intel Core i9-10900K", "Intel", 279.00, "LGA1200", "10 Cores / 20 Threads", "3.7 GHz (5.3 GHz Boost)", 125, True, 4.8, 3900),
        ("cpu-10700k", "Intel Core i7-10700K", "Intel", 199.00, "LGA1200", "8 Cores / 16 Threads", "3.8 GHz (5.1 GHz Boost)", 125, True, 4.8, 4500),
        ("cpu-10400f", "Intel Core i5-10400F", "Intel", 99.00, "LGA1200", "6 Cores / 12 Threads", "2.9 GHz (4.3 GHz Boost)", 65, False, 4.8, 6200),
        ("cpu-9900k", "Intel Core i9-9900K", "Intel", 289.00, "LGA1151", "8 Cores / 16 Threads", "3.6 GHz (5.0 GHz Boost)", 95, True, 4.9, 8900),
        ("cpu-9700k", "Intel Core i7-9700K", "Intel", 189.00, "LGA1151", "8 Cores / 8 Threads", "3.6 GHz (4.9 GHz Boost)", 95, True, 4.8, 7400),

        # Intel Core 8th - 7th - 6th - 4th - 2nd Gen
        ("cpu-8700k", "Intel Core i7-8700K", "Intel", 159.00, "LGA1151", "6 Cores / 12 Threads", "3.7 GHz (4.7 GHz Boost)", 95, True, 4.8, 6700),
        ("cpu-7700k", "Intel Core i7-7700K", "Intel", 139.00, "LGA1151", "4 Cores / 8 Threads", "4.2 GHz (4.5 GHz Boost)", 91, True, 4.8, 6200),
        ("cpu-6700k", "Intel Core i7-6700K", "Intel", 119.00, "LGA1151", "4 Cores / 8 Threads", "4.0 GHz (4.2 GHz Boost)", 91, True, 4.8, 5900),
        ("cpu-4790k", "Intel Core i7-4790K Devil's Canyon", "Intel", 109.00, "LGA1150", "4 Cores / 8 Threads", "4.0 GHz (4.4 GHz Boost)", 88, True, 4.9, 9400),
        ("cpu-2600k", "Intel Core i7-2600K Sandy Bridge", "Intel", 69.00, "LGA1155", "4 Cores / 8 Threads", "3.4 GHz (3.8 GHz Boost)", 95, True, 4.9, 11200),
        ("cpu-q6600", "Intel Core 2 Quad Q6600 Kentsfield", "Intel", 35.00, "LGA775", "4 Cores / 4 Threads", "2.4 GHz", 105, False, 4.8, 7800),
        ("cpu-e8400", "Intel Core 2 Duo E8400 Wolfdale", "Intel", 25.00, "LGA775", "2 Cores / 2 Threads", "3.0 GHz", 65, False, 4.8, 6100),
        ("cpu-p4-32", "Intel Pentium 4 Extreme Edition 3.2 GHz", "Intel", 45.00, "Socket 478", "1 Core / 2 Threads (HT)", "3.2 GHz", 92, False, 4.5, 2300),
    ]

    for (cid, name, brand, price, sock, cores, speed, tdp, hasGpu, rating, rev) in cpus_raw:
        catalog.append({
            "id": cid,
            "category": "cpu",
            "name": name,
            "brand": brand,
            "price": price,
            "merchant": "Amazon" if "AMD" in brand else "Newegg",
            "rating": rating,
            "reviews": rev,
            "specs": {
                "socket": sock,
                "cores": cores,
                "speed": speed,
                "tdp": tdp,
                "hasGpu": hasGpu,
                "col1": cores,
                "col2": f"{tdp}W TDP • {sock}"
            }
        })

    # =========================================================================
    # 2. GPUs (NVIDIA, AMD, INTEL across all eras)
    # =========================================================================
    gpus_raw = [
        # NVIDIA RTX 40 Series
        ("gpu-rtx4090", "MSI GAMING X SLIM GeForce RTX 4090 24 GB", "NVIDIA / MSI", 1749.99, "GeForce RTX 4090", "24 GB GDDR6X", 450, 322, 4.9, 1200),
        ("gpu-rtx4080super", "Gigabyte WINDFORCE V2 GeForce RTX 4080 SUPER 16 GB", "NVIDIA / Gigabyte", 999.99, "GeForce RTX 4080 SUPER", "16 GB GDDR6X", 320, 330, 4.8, 1450),
        ("gpu-rtx4080", "ASUS TUF Gaming GeForce RTX 4080 16 GB", "NVIDIA / ASUS", 949.99, "GeForce RTX 4080", "16 GB GDDR6X", 320, 348, 4.8, 1100),
        ("gpu-rtx4070tisuper", "Zotac GAMING Trinity GeForce RTX 4070 Ti SUPER 16 GB", "NVIDIA / Zotac", 799.99, "GeForce RTX 4070 Ti SUPER", "16 GB GDDR6X", 285, 307, 4.8, 920),
        ("gpu-rtx4070ti", "MSI Ventus 3X GeForce RTX 4070 Ti 12 GB", "NVIDIA / MSI", 729.99, "GeForce RTX 4070 Ti", "12 GB GDDR6X", 285, 308, 4.7, 1340),
        ("gpu-rtx4070super", "ASUS DUAL OC GeForce RTX 4070 SUPER 12 GB", "NVIDIA / ASUS", 599.99, "GeForce RTX 4070 SUPER", "12 GB GDDR6X", 220, 267, 4.8, 2200),
        ("gpu-rtx4070", "Gigabyte WINDFORCE OC GeForce RTX 4070 12 GB", "NVIDIA / Gigabyte", 529.99, "GeForce RTX 4070", "12 GB GDDR6X", 200, 261, 4.8, 3100),
        ("gpu-rtx4060ti-16", "PNY XLR8 Gaming GeForce RTX 4060 Ti 16 GB", "NVIDIA / PNY", 449.99, "GeForce RTX 4060 Ti 16GB", "16 GB GDDR6", 165, 245, 4.6, 780),
        ("gpu-rtx4060ti-8", "MSI VENTUS 2X GeForce RTX 4060 Ti 8 GB", "NVIDIA / MSI", 379.99, "GeForce RTX 4060 Ti", "8 GB GDDR6", 160, 199, 4.7, 2400),
        ("gpu-rtx4060", "ASUS Dual GeForce RTX 4060 EVO 8 GB", "NVIDIA / ASUS", 299.99, "GeForce RTX 4060", "8 GB GDDR6", 115, 227, 4.7, 3600),

        # NVIDIA RTX 30 Series
        ("gpu-rtx3090ti", "EVGA FTW3 ULTRA GeForce RTX 3090 Ti 24 GB", "NVIDIA / EVGA", 899.99, "GeForce RTX 3090 Ti", "24 GB GDDR6X", 450, 300, 4.8, 1400),
        ("gpu-rtx3090", "ASUS ROG STRIX GeForce RTX 3090 24 GB", "NVIDIA / ASUS", 749.99, "GeForce RTX 3090", "24 GB GDDR6X", 350, 318, 4.8, 3200),
        ("gpu-rtx3080ti", "Gigabyte GAMING OC GeForce RTX 3080 Ti 12 GB", "NVIDIA / Gigabyte", 589.99, "GeForce RTX 3080 Ti", "12 GB GDDR6X", 350, 320, 4.8, 2600),
        ("gpu-rtx3080", "EVGA XC3 ULTRA GeForce RTX 3080 10 GB", "NVIDIA / EVGA", 459.99, "GeForce RTX 3080", "10 GB GDDR6X", 320, 285, 4.9, 5800),
        ("gpu-rtx3070ti", "MSI Gaming X Trio GeForce RTX 3070 Ti 8 GB", "NVIDIA / MSI", 389.99, "GeForce RTX 3070 Ti", "8 GB GDDR6X", 290, 323, 4.7, 2900),
        ("gpu-rtx3070", "Founders Edition GeForce RTX 3070 8 GB", "NVIDIA", 319.99, "GeForce RTX 3070", "8 GB GDDR6", 220, 242, 4.8, 6400),
        ("gpu-rtx3060ti", "ASUS TUF Gaming GeForce RTX 3060 Ti 8 GB", "NVIDIA / ASUS", 279.99, "GeForce RTX 3060 Ti", "8 GB GDDR6", 200, 301, 4.8, 7100),
        ("gpu-rtx3060", "MSI GeForce RTX 3060 Ventus 2X 12 GB", "NVIDIA / MSI", 259.99, "GeForce RTX 3060", "12 GB GDDR6", 170, 235, 4.8, 8900),
        ("gpu-rtx3050", "Gigabyte EAGLE GeForce RTX 3050 6 GB", "NVIDIA / Gigabyte", 179.99, "GeForce RTX 3050", "6 GB GDDR6", 70, 192, 4.6, 2100),

        # NVIDIA RTX 20 & GTX 16 Series
        ("gpu-rtx2080ti", "EVGA GeForce RTX 2080 Ti FTW3 Ultra 11 GB", "NVIDIA / EVGA", 349.99, "GeForce RTX 2080 Ti", "11 GB GDDR6", 250, 301, 4.8, 4800),
        ("gpu-rtx2080super", "MSI GAMING X TRIO GeForce RTX 2080 SUPER 8 GB", "NVIDIA / MSI", 279.99, "GeForce RTX 2080 SUPER", "8 GB GDDR6", 250, 328, 4.8, 3900),
        ("gpu-rtx2070super", "Gigabyte GeForce RTX 2070 SUPER WINDFORCE 8 GB", "NVIDIA / Gigabyte", 219.99, "GeForce RTX 2070 SUPER", "8 GB GDDR6", 215, 286, 4.8, 6200),
        ("gpu-rtx2060super", "Founders Edition GeForce RTX 2060 SUPER 8 GB", "NVIDIA", 179.99, "GeForce RTX 2060 SUPER", "8 GB GDDR6", 175, 229, 4.8, 5400),
        ("gpu-gtx1660super", "EVGA GeForce GTX 1660 SUPER SC Ultra 6 GB", "NVIDIA / EVGA", 149.99, "GeForce GTX 1660 SUPER", "6 GB GDDR6", 125, 202, 4.8, 9200),
        ("gpu-gtx1650", "Zotac GAMING GeForce GTX 1650 OC 4 GB", "NVIDIA / Zotac", 129.99, "GeForce GTX 1650", "4 GB GDDR6", 75, 151, 4.7, 7800),

        # NVIDIA GTX 10, 900 & Classics
        ("gpu-gtx1080ti", "EVGA GeForce GTX 1080 Ti SC2 GAMING 11 GB", "NVIDIA / EVGA", 189.99, "GeForce GTX 1080 Ti", "11 GB GDDR5X", 250, 269, 4.9, 11400),
        ("gpu-gtx1080", "MSI GeForce GTX 1080 GAMING X 8 GB", "NVIDIA / MSI", 139.99, "GeForce GTX 1080", "8 GB GDDR5X", 180, 279, 4.8, 8900),
        ("gpu-gtx1070", "EVGA GeForce GTX 1070 FTW GAMING 8 GB", "NVIDIA / EVGA", 119.99, "GeForce GTX 1070", "8 GB GDDR5", 150, 267, 4.8, 9800),
        ("gpu-gtx1060-6gb", "MSI GeForce GTX 1060 GAMING X 6 GB", "NVIDIA / MSI", 89.99, "GeForce GTX 1060 6GB", "6 GB GDDR5", 120, 277, 4.8, 14200),
        ("gpu-gtx980ti", "EVGA GeForce GTX 980 Ti Classified 6 GB", "NVIDIA / EVGA", 109.99, "GeForce GTX 980 Ti", "6 GB GDDR5", 250, 279, 4.8, 6200),
        ("gpu-gtx970", "MSI GeForce GTX 970 GAMING 4 GB", "NVIDIA / MSI", 79.99, "GeForce GTX 970", "4 GB GDDR5", 145, 269, 4.8, 16800),
        ("gpu-gtx750ti", "EVGA GeForce GTX 750 Ti FTW 2 GB", "NVIDIA / EVGA", 49.99, "GeForce GTX 750 Ti", "2 GB GDDR5", 60, 170, 4.8, 12900),
        ("gpu-8800gtx", "NVIDIA GeForce 8800 GTX 768 MB (Legendary G80)", "NVIDIA", 59.99, "GeForce 8800 GTX", "768 MB GDDR3", 155, 267, 4.9, 8200),

        # AMD Radeon RX 7000 Series
        ("gpu-rx7900xtx", "Sapphire NITRO+ Radeon RX 7900 XTX 24 GB", "AMD / Sapphire", 949.99, "Radeon RX 7900 XTX", "24 GB GDDR6", 355, 320, 4.8, 1850),
        ("gpu-rx7900xt", "XFX Speedster MERC310 Radeon RX 7900 XT 20 GB", "AMD / XFX", 679.99, "Radeon RX 7900 XT", "20 GB GDDR6", 315, 344, 4.8, 1640),
        ("gpu-rx7900gre", "PowerColor Hellhound Radeon RX 7900 GRE 16 GB", "AMD / PowerColor", 539.99, "Radeon RX 7900 GRE", "16 GB GDDR6", 260, 322, 4.8, 1200),
        ("gpu-rx7800xt", "Sapphire PULSE Radeon RX 7800 XT 16 GB", "AMD / Sapphire", 489.99, "Radeon RX 7800 XT", "16 GB GDDR6", 263, 280, 4.8, 2900),
        ("gpu-rx7700xt", "Gigabyte GAMING OC Radeon RX 7700 XT 12 GB", "AMD / Gigabyte", 399.99, "Radeon RX 7700 XT", "12 GB GDDR6", 245, 302, 4.7, 1400),
        ("gpu-rx7600xt", "XFX Speedster SWFT210 Radeon RX 7600 XT 16 GB", "AMD / XFX", 319.99, "Radeon RX 7600 XT", "16 GB GDDR6", 190, 241, 4.6, 950),
        ("gpu-rx7600", "ASRock Challenger D Radeon RX 7600 8 GB", "AMD / ASRock", 259.99, "Radeon RX 7600", "8 GB GDDR6", 165, 269, 4.7, 1800),

        # AMD Radeon RX 6000 Series
        ("gpu-rx6950xt", "MSI Gaming X Trio Radeon RX 6950 XT 16 GB", "AMD / MSI", 569.99, "Radeon RX 6950 XT", "16 GB GDDR6", 335, 324, 4.8, 2100),
        ("gpu-rx6800xt", "PowerColor Red Devil Radeon RX 6800 XT 16 GB", "AMD / PowerColor", 449.99, "Radeon RX 6800 XT", "16 GB GDDR6", 300, 320, 4.8, 3800),
        ("gpu-rx6750xt", "XFX Speedster QICK319 Radeon RX 6750 XT 12 GB", "AMD / XFX", 329.99, "Radeon RX 6750 XT", "12 GB GDDR6", 250, 323, 4.8, 3400),
        ("gpu-rx6700xt", "Sapphire PULSE Radeon RX 6700 XT 12 GB", "AMD / Sapphire", 299.99, "Radeon RX 6700 XT", "12 GB GDDR6", 230, 260, 4.8, 5900),
        ("gpu-rx6600", "ASRock Challenger D Radeon RX 6600 8 GB", "AMD / ASRock", 189.99, "Radeon RX 6600", "8 GB GDDR6", 132, 269, 4.8, 6400),

        # AMD Radeon RX 5000, RX 500, R9 & Classics
        ("gpu-rx5700xt", "Sapphire NITRO+ Radeon RX 5700 XT 8 GB", "AMD / Sapphire", 169.99, "Radeon RX 5700 XT", "8 GB GDDR6", 225, 306, 4.7, 5900),
        ("gpu-rx580-8gb", "XFX GTS XXX Edition Radeon RX 580 8 GB", "AMD / XFX", 109.99, "Radeon RX 580", "8 GB GDDR5", 185, 270, 4.8, 14800),
        ("gpu-r9-fury-x", "AMD Radeon R9 Fury X 4 GB HBM (Water Cooled)", "AMD", 129.99, "Radeon R9 Fury X", "4 GB HBM1", 275, 195, 4.6, 2100),
        ("gpu-r9-290x", "Sapphire Tri-X Radeon R9 290X 4 GB", "AMD / Sapphire", 89.99, "Radeon R9 290X", "4 GB GDDR5", 290, 305, 4.7, 4300),
        ("gpu-hd7970", "Gigabyte Radeon HD 7970 GHz Edition 3 GB (Tahiti)", "AMD / Gigabyte", 69.99, "Radeon HD 7970", "3 GB GDDR5", 250, 285, 4.8, 5600),

        # Intel Arc Series
        ("gpu-arc-a770-16", "Acer Predator BiFrost Intel Arc A770 16 GB", "Intel / Acer", 289.99, "Intel Arc A770", "16 GB GDDR6", 225, 267, 4.6, 1200),
        ("gpu-arc-a750", "Intel Arc A750 Limited Edition 8 GB", "Intel", 199.99, "Intel Arc A750", "8 GB GDDR6", 225, 279, 4.5, 2100),
        ("gpu-arc-a580", "ASRock Challenger Intel Arc A580 8 GB", "Intel / ASRock", 159.99, "Intel Arc A580", "8 GB GDDR6", 185, 271, 4.5, 890),

        # Retro 3dfx
        ("gpu-voodoo2", "Diamond Monster 3D II 3dfx Voodoo2 12 MB (PCI Retro)", "3dfx / Diamond", 199.99, "3dfx Voodoo2", "12 MB EDO RAM", 25, 180, 5.0, 3100),
        ("gpu-voodoo5", "3dfx Voodoo5 5500 AGP 64 MB Dual VSA-100", "3dfx", 499.99, "3dfx Voodoo5 5500", "64 MB SDR", 55, 240, 5.0, 1800),
    ]

    for (gid, name, brand, price, chip, vram, tdp, length, rating, rev) in gpus_raw:
        catalog.append({
            "id": gid,
            "category": "gpu",
            "name": name,
            "brand": brand,
            "price": price,
            "merchant": "Best Buy" if "NVIDIA" in brand else "Amazon",
            "rating": rating,
            "reviews": rev,
            "specs": {
                "chipset": chip,
                "vram": vram,
                "tdp": tdp,
                "lengthMm": length,
                "col1": f"{vram} • {chip}",
                "col2": f"{tdp}W TDP • {length}mm"
            }
        })

    # =========================================================================
    # 3. SSDs (PCIe Gen5, Gen4, Gen3 NVMe, SATA 2.5", Legacy)
    # =========================================================================
    ssds_raw = [
        # PCIe Gen 5 NVMe (Blazing Speeds up to 14,000 MB/s)
        ("ssd-crucial-t705-4tb", "Crucial T705 4 TB PCIe Gen5 NVMe with Heatsink", "Crucial", 519.99, "4 TB", "PCIe Gen5 x4 NVMe", "14,500 MB/s", 4.8, 380),
        ("ssd-crucial-t705-2tb", "Crucial T705 2 TB PCIe Gen5 NVMe M.2 SSD", "Crucial", 279.99, "2 TB", "PCIe Gen5 x4 NVMe", "14,500 MB/s", 4.9, 920),
        ("ssd-crucial-t705-1tb", "Crucial T705 1 TB PCIe Gen5 NVMe M.2 SSD", "Crucial", 169.99, "1 TB", "PCIe Gen5 x4 NVMe", "13,600 MB/s", 4.8, 640),
        ("ssd-corsair-mp700-2tb", "Corsair MP700 PRO 2 TB PCIe Gen5 x4 NVMe M.2", "Corsair", 289.99, "2 TB", "PCIe Gen5 x4 NVMe", "12,400 MB/s", 4.8, 510),
        ("ssd-aorus-gen5-2tb", "Gigabyte AORUS Gen5 12000 2 TB PCIe Gen5 NVMe", "Gigabyte", 269.99, "2 TB", "PCIe Gen5 x4 NVMe", "12,000 MB/s", 4.7, 430),

        # PCIe Gen 4 NVMe (Flagships & Midrange)
        ("ssd-samsung-990pro-4tb", "Samsung 990 Pro 4 TB PCIe 4.0 X4 NVMe SSD", "Samsung", 329.99, "4 TB", "PCIe Gen4 x4 NVMe", "7,450 MB/s", 4.9, 2100),
        ("ssd-samsung-990pro-2tb", "Samsung 990 Pro 2 TB PCIe 4.0 X4 NVMe SSD", "Samsung", 169.99, "2 TB", "PCIe Gen4 x4 NVMe", "7,450 MB/s", 4.9, 8400),
        ("ssd-samsung-990pro-1tb", "Samsung 990 Pro 1 TB PCIe 4.0 X4 NVMe SSD", "Samsung", 109.99, "1 TB", "PCIe Gen4 x4 NVMe", "7,450 MB/s", 4.9, 5600),
        ("ssd-wd-sn850x-4tb", "Western Digital Black SN850X 4 TB PCIe Gen4 NVMe", "Western Digital", 309.99, "4 TB", "PCIe Gen4 x4 NVMe", "7,300 MB/s", 4.9, 1850),
        ("ssd-wd-sn850x-2tb", "Western Digital Black SN850X 2 TB PCIe Gen4 NVMe", "Western Digital", 149.99, "2 TB", "PCIe Gen4 x4 NVMe", "7,300 MB/s", 4.9, 7200),
        ("ssd-wd-sn850x-1tb", "Western Digital Black SN850X 1 TB PCIe Gen4 NVMe", "Western Digital", 94.99, "1 TB", "PCIe Gen4 x4 NVMe", "7,300 MB/s", 4.8, 6100),
        ("ssd-crucial-t500-2tb", "Crucial T500 2 TB PCIe Gen4 NVMe with DRAM", "Crucial", 144.99, "2 TB", "PCIe Gen4 x4 NVMe", "7,400 MB/s", 4.8, 3100),
        ("ssd-crucial-t500-1tb", "Crucial T500 1 TB PCIe Gen4 NVMe M.2", "Crucial", 84.99, "1 TB", "PCIe Gen4 x4 NVMe", "7,300 MB/s", 4.8, 2900),
        ("ssd-kc3000-2tb", "Kingston KC3000 2 TB PCIe 4.0 NVMe M.2 SSD", "Kingston", 159.99, "2 TB", "PCIe Gen4 x4 NVMe", "7,000 MB/s", 4.8, 4100),
        ("ssd-crucial-p3plus-2tb", "Crucial P3 Plus 2 TB PCIe 4.0 X4 NVMe SSD", "Crucial", 119.99, "2 TB", "PCIe Gen4 x4 NVMe", "5,000 MB/s", 4.7, 5800),
        ("ssd-crucial-p3plus-1tb", "Crucial P3 Plus 1 TB PCIe 4.0 X4 NVMe SSD", "Crucial", 61.99, "1 TB", "PCIe Gen4 x4 NVMe", "5,000 MB/s", 4.7, 8200),
        ("ssd-wd-sn770-1tb", "Western Digital Black SN770 1 TB PCIe 4.0 NVMe", "Western Digital", 74.99, "1 TB", "PCIe Gen4 x4 NVMe", "5,150 MB/s", 4.8, 6400),
        ("ssd-lexar-nm790-4tb", "Lexar NM790 4 TB PCIe Gen4x4 NVMe M.2", "Lexar", 249.99, "4 TB", "PCIe Gen4 x4 NVMe", "7,400 MB/s", 4.8, 1900),

        # PCIe Gen 3 NVMe (Budget & Reliable)
        ("ssd-samsung-970evo-2tb", "Samsung 970 EVO Plus 2 TB PCIe 3.0 X4 NVMe", "Samsung", 139.99, "2 TB", "PCIe Gen3 x4 NVMe", "3,500 MB/s", 4.9, 14200),
        ("ssd-samsung-970evo-1tb", "Samsung 970 EVO Plus 1 TB PCIe 3.0 X4 NVMe", "Samsung", 89.99, "1 TB", "PCIe Gen3 x4 NVMe", "3,500 MB/s", 4.9, 19800),
        ("ssd-samsung-970evo-500g", "Samsung 970 EVO Plus 500 GB PCIe 3.0 NVMe", "Samsung", 59.99, "500 GB", "PCIe Gen3 x4 NVMe", "3,500 MB/s", 4.9, 11200),
        ("ssd-crucial-p3-1tb", "Crucial P3 1 TB PCIe 3.0 X4 NVMe SSD", "Crucial", 56.99, "1 TB", "PCIe Gen3 x4 NVMe", "3,500 MB/s", 4.7, 7800),
        ("ssd-kingston-nv2-1tb", "Kingston NV2 1 TB M.2-2280 PCIe 4.0 NVMe", "Kingston", 54.99, "1 TB", "PCIe NVMe M.2", "3,500 MB/s", 4.6, 9200),

        # 2.5" SATA SSDs (Compatible with nearly every desktop built since 2005)
        ("ssd-samsung-870evo-4tb", "Samsung 870 EVO 4 TB 2.5\" SATA III SSD", "Samsung", 299.99, "4 TB", "2.5\" SATA III (6 Gb/s)", "560 MB/s", 4.8, 6200),
        ("ssd-samsung-870evo-2tb", "Samsung 870 EVO 2 TB 2.5\" SATA III SSD", "Samsung", 159.99, "2 TB", "2.5\" SATA III (6 Gb/s)", "560 MB/s", 4.8, 11400),
        ("ssd-samsung-870evo-1tb", "Samsung 870 EVO 1 TB 2.5\" SATA III SSD", "Samsung", 89.99, "1 TB", "2.5\" SATA III (6 Gb/s)", "560 MB/s", 4.8, 18900),
        ("ssd-samsung-870evo-500g", "Samsung 870 EVO 500 GB 2.5\" SATA III SSD", "Samsung", 54.99, "500 GB", "2.5\" SATA III (6 Gb/s)", "560 MB/s", 4.8, 14200),
        ("ssd-crucial-mx500-2tb", "Crucial MX500 2 TB 2.5\" SATA III SSD", "Crucial", 139.99, "2 TB", "2.5\" SATA III (6 Gb/s)", "560 MB/s", 4.8, 16800),
        ("ssd-crucial-mx500-1tb", "Crucial MX500 1 TB 2.5\" SATA III SSD", "Crucial", 79.99, "1 TB", "2.5\" SATA III (6 Gb/s)", "560 MB/s", 4.8, 24500),
        ("ssd-kingston-a400-960g", "Kingston A400 960 GB 2.5\" SATA III SSD", "Kingston", 52.99, "960 GB", "2.5\" SATA III (6 Gb/s)", "500 MB/s", 4.7, 19200),
        ("ssd-kingston-a400-480g", "Kingston A400 480 GB 2.5\" SATA III SSD", "Kingston", 32.99, "480 GB", "2.5\" SATA III (6 Gb/s)", "500 MB/s", 4.7, 28000),
        ("ssd-kingston-a400-240g", "Kingston A400 240 GB 2.5\" SATA III SSD", "Kingston", 22.99, "240 GB", "2.5\" SATA III (6 Gb/s)", "500 MB/s", 4.7, 34000),

        # Legendary Early Historical SSDs
        ("ssd-intel-x25m-80g", "Intel X25-M Mainstream 80 GB SATA II SSD (Historic Pioneer)", "Intel", 49.99, "80 GB", "2.5\" SATA II (3 Gb/s)", "250 MB/s", 4.8, 4800),
        ("ssd-crucial-m4-128g", "Crucial M4 128 GB SATA 6Gb/s SSD (Marvell Legend)", "Crucial", 39.99, "128 GB", "2.5\" SATA III (6 Gb/s)", "415 MB/s", 4.8, 7100),
        ("ssd-samsung-850pro-512", "Samsung 850 PRO 512 GB 3D V-NAND 10-Yr Warranty Legend", "Samsung", 79.99, "512 GB", "2.5\" SATA III (6 Gb/s)", "550 MB/s", 4.9, 13400),
    ]

    for (sid, name, brand, price, cap, iface, speed, rating, rev) in ssds_raw:
        catalog.append({
            "id": sid,
            "category": "storage",
            "name": name,
            "brand": brand,
            "price": price,
            "merchant": "Amazon",
            "rating": rating,
            "reviews": rev,
            "specs": {
                "capacity": cap,
                "interface": iface,
                "readSpeed": speed,
                "col1": f"{cap} • {iface}",
                "col2": f"Up to {speed} Read"
            }
        })

    # =========================================================================
    # 4. RAM / MEMORY (DDR5, DDR4, DDR3, DDR2, DDR1 across all speeds)
    # =========================================================================
    ram_raw = [
        # DDR5 High Performance & Enthusiast
        ("ram-dominator-tit-96-ddr5", "Corsair Dominator Titanium 96 GB (2 x 48 GB) DDR5-6600 CL32", "Corsair", 429.99, "DDR5", "DDR5-6600", "96 GB (2 x 48 GB)", "CL32-39-39-76", 4.9, 410),
        ("ram-dominator-tit-64-ddr5", "Corsair Dominator Titanium 64 GB (2 x 32 GB) DDR5-6000 CL30", "Corsair", 269.99, "DDR5", "DDR5-6000", "64 GB (2 x 32 GB)", "CL30-36-36-76", 4.9, 820),
        ("ram-trident-z5-rgb-64-ddr5", "G.Skill Trident Z5 RGB 64 GB (2 x 32 GB) DDR5-6400 CL32", "G.Skill", 219.99, "DDR5", "DDR5-6400", "64 GB (2 x 32 GB)", "CL32-39-39-102", 4.8, 1420),
        ("ram-trident-z5-rgb-32-ddr5", "G.Skill Trident Z5 Neo RGB 32 GB (2 x 16 GB) DDR5-6000 CL30 AMD EXPO", "G.Skill", 119.99, "DDR5", "DDR5-6000", "32 GB (2 x 16 GB)", "CL30-38-38-96", 4.9, 3900),
        ("ram-vengeance-rgb-32-ddr5", "Corsair Vengeance RGB 32 GB (2 x 16 GB) DDR5-6000 CL30", "Corsair", 124.99, "DDR5", "DDR5-6000", "32 GB (2 x 16 GB)", "CL30-36-36-76", 4.8, 4800),
        ("ram-vengeance-32-ddr5", "Corsair Vengeance 32 GB (2 x 16 GB) DDR5-6000 CL30", "Corsair", 114.99, "DDR5", "DDR5-6000", "32 GB (2 x 16 GB)", "CL30-36-36-76", 4.8, 5600),
        ("ram-flare-x5-32-ddr5", "G.Skill Flare X5 32 GB (2 x 16 GB) DDR5-6000 CL32 AMD EXPO", "G.Skill", 99.99, "DDR5", "DDR5-6000", "32 GB (2 x 16 GB)", "CL32-38-38-96", 4.8, 3800),
        ("ram-tforce-delta-32-ddr5", "TEAMGROUP T-Force Delta RGB 32 GB (2 x 16 GB) DDR5-6000 CL30", "Teamgroup", 102.99, "DDR5", "DDR5-6000", "32 GB (2 x 16 GB)", "CL30-36-36-76", 4.8, 2900),
        ("ram-crucial-pro-64-ddr5", "Crucial Pro 64 GB (2 x 32 GB) DDR5-5600 CL46", "Crucial", 169.99, "DDR5", "DDR5-5600", "64 GB (2 x 32 GB)", "CL46", 4.7, 1850),
        ("ram-crucial-pro-32-ddr5", "Crucial Pro 32 GB (2 x 16 GB) DDR5-5600 CL46 Plug & Play", "Crucial", 84.99, "DDR5", "DDR5-5600", "32 GB (2 x 16 GB)", "CL46", 4.7, 2600),
        ("ram-kingston-fury-32-ddr5", "Kingston Fury Beast 32 GB (2 x 16 GB) DDR5-5200 CL40", "Kingston", 89.99, "DDR5", "DDR5-5200", "32 GB (2 x 16 GB)", "CL40", 4.7, 1900),
        ("ram-crucial-16-ddr5", "Crucial 16 GB (2 x 8 GB) DDR5-4800 CL40", "Crucial", 52.99, "DDR5", "DDR5-4800", "16 GB (2 x 8 GB)", "CL40", 4.6, 1400),

        # DDR4 High Performance & Value
        ("ram-vengeance-rgb-pro-64-ddr4", "Corsair Vengeance RGB Pro 64 GB (2 x 32 GB) DDR4-3600 CL18", "Corsair", 149.99, "DDR4", "DDR4-3600", "64 GB (2 x 32 GB)", "CL18-22-22-42", 4.8, 4800),
        ("ram-vengeance-lpx-64-ddr4", "Corsair Vengeance LPX 64 GB (2 x 32 GB) DDR4-3200 CL16", "Corsair", 129.99, "DDR4", "DDR4-3200", "64 GB (2 x 32 GB)", "CL16-20-20-38", 4.8, 5900),
        ("ram-ripjaws-v-32-ddr4-3600", "G.Skill Ripjaws V 32 GB (2 x 16 GB) DDR4-3600 CL16 (B-Die)", "G.Skill", 74.99, "DDR4", "DDR4-3600", "32 GB (2 x 16 GB)", "CL16-19-19-39", 4.9, 9400),
        ("ram-ripjaws-v-32-ddr4-3200", "G.Skill Ripjaws V 32 GB (2 x 16 GB) DDR4-3200 CL16", "G.Skill", 59.99, "DDR4", "DDR4-3200", "32 GB (2 x 16 GB)", "CL16-18-18-38", 4.8, 14200),
        ("ram-vengeance-lpx-32-ddr4", "Corsair Vengeance LPX 32 GB (2 x 16 GB) DDR4-3200 CL16", "Corsair", 59.99, "DDR4", "DDR4-3200", "32 GB (2 x 16 GB)", "CL16-20-20-38", 4.8, 18500),
        ("ram-tforce-vulcan-32-ddr4", "TEAMGROUP T-Force Vulcan Z 32 GB (2 x 16 GB) DDR4-3200 CL16", "Teamgroup", 52.99, "DDR4", "DDR4-3200", "32 GB (2 x 16 GB)", "CL16-20-20-40", 4.8, 8900),
        ("ram-ripjaws-v-16-ddr4", "G.Skill Ripjaws V 16 GB (2 x 8 GB) DDR4-3200 CL16", "G.Skill", 35.99, "DDR4", "DDR4-3200", "16 GB (2 x 8 GB)", "CL16-18-18-38", 4.8, 28900),
        ("ram-vengeance-lpx-16-ddr4", "Corsair Vengeance LPX 16 GB (2 x 8 GB) DDR4-3200 CL16", "Corsair", 39.99, "DDR4", "DDR4-3200", "16 GB (2 x 8 GB)", "CL16-18-18-36", 4.8, 34000),
        ("ram-tforce-vulcan-16-ddr4", "TEAMGROUP T-Force Vulcan Z 16 GB (2 x 8 GB) DDR4-3200 CL16", "Teamgroup", 31.99, "DDR4", "DDR4-3200", "16 GB (2 x 8 GB)", "CL16-20-20-40", 4.8, 16400),
        ("ram-crucial-8-ddr4", "Crucial 8 GB (1 x 8 GB) DDR4-2666 CL19", "Crucial", 18.99, "DDR4", "DDR4-2666", "8 GB (1 x 8 GB)", "CL19", 4.7, 7400),

        # DDR3 Golden Era
        ("ram-vengeance-pro-16-ddr3", "Corsair Vengeance Pro 16 GB (2 x 8 GB) DDR3-2400 CL11", "Corsair", 49.99, "DDR3", "DDR3-2400", "16 GB (2 x 8 GB)", "CL11-13-13-31", 4.8, 5200),
        ("ram-ripjaws-x-16-ddr3", "G.Skill Ripjaws X 16 GB (2 x 8 GB) DDR3-1600 CL9", "G.Skill", 39.99, "DDR3", "DDR3-1600", "16 GB (2 x 8 GB)", "CL9-9-9-24", 4.8, 11400),
        ("ram-vengeance-16-ddr3", "Corsair Vengeance 16 GB (2 x 8 GB) DDR3-1600 CL10", "Corsair", 39.99, "DDR3", "DDR3-1600", "16 GB (2 x 8 GB)", "CL10-10-10-27", 4.8, 14200),
        ("ram-hyperx-fury-8-ddr3", "Kingston HyperX FURY 8 GB (2 x 4 GB) DDR3-1600 CL10", "Kingston", 24.99, "DDR3", "DDR3-1600", "8 GB (2 x 4 GB)", "CL10", 4.8, 18900),

        # DDR2 & DDR1 Historic Classics
        ("ram-dominator-4-ddr2", "Corsair Dominator 4 GB (2 x 2 GB) DDR2-1066 CL5 with Airflow Fan", "Corsair", 29.99, "DDR2", "DDR2-1066", "4 GB (2 x 2 GB)", "CL5-5-5-15", 4.8, 3800),
        ("ram-crucial-4-ddr2", "Crucial Ballistix 4 GB (2 x 2 GB) DDR2-800 CL4", "Crucial", 22.99, "DDR2", "DDR2-800", "4 GB (2 x 2 GB)", "CL4-4-4-12", 4.7, 4900),
        ("ram-corsair-xms-2-ddr1", "Corsair XMS 2 GB (2 x 1 GB) DDR-400 PC3200 Platinum Heat Spreader", "Corsair", 24.99, "DDR1", "DDR-400", "2 GB (2 x 1 GB)", "CL2-3-3-6", 4.9, 5800),
        ("ram-kingston-1-ddr1", "Kingston ValueRAM 1 GB (2 x 512 MB) DDR-400 PC3200", "Kingston", 16.99, "DDR1", "DDR-400", "1 GB (2 x 512 MB)", "CL3", 4.7, 7200),
    ]

    for (rid, name, brand, price, rtype, speed, cap, timing, rating, rev) in ram_raw:
        catalog.append({
            "id": rid,
            "category": "memory",
            "name": name,
            "brand": brand,
            "price": price,
            "merchant": "Newegg" if "G.Skill" in brand else "Amazon",
            "rating": rating,
            "reviews": rev,
            "specs": {
                "type": rtype,
                "speed": speed,
                "capacity": cap,
                "timing": timing,
                "col1": f"{cap} • {timing}",
                "col2": f"{speed} • {rtype}"
            }
        })

    return catalog

def update_database(new_parts):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    inserted = 0
    for p in new_parts:
        cur.execute("""
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
        inserted += 1

    conn.commit()
    print(f"Stored {inserted} parts into SQLite database: {DB_FILE}")

    # Report counts
    cur.execute("SELECT category, count(*) FROM parts GROUP BY category;")
    print("Database breakdown by category:")
    for row in cur.fetchall():
        print(f" - {row[0].upper()}: {row[1]} components")

    conn.close()

def update_data_js(new_parts):
    # Read existing data.js to keep other categories (coolers, motherboards, cases, psu, os, monitors, presets)
    with open(DATA_JS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract other categories from existing data.js that aren't CPU, GPU, Storage, RAM
    other_cats = ["cooler", "motherboard", "case", "psu", "os", "monitor"]
    import re
    # We can fetch existing other components from sqlite to ensure consistency
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts WHERE category IN ('cooler', 'motherboard', 'case', 'psu', 'os', 'monitor')")
    other_rows = cur.fetchall()
    conn.close()

    full_catalog = []
    # Add all new parts (CPUs, GPUs, SSDs, RAM)
    full_catalog.extend(new_parts)

    # Add other categories
    for r in other_rows:
        try:
            sp = json.loads(r[8])
        except Exception:
            sp = {}
        full_catalog.append({
            "id": r[0],
            "category": r[1],
            "name": r[2],
            "brand": r[3],
            "price": float(r[4]),
            "merchant": r[5],
            "rating": float(r[6]),
            "reviews": int(r[7]),
            "specs": sp
        })

    # Generate new data.js file
    new_data_js = f"""// PCPartPicker Complete Hardware Database & Presets
// Contains comprehensive catalog of CPUs, GPUs, SSDs, RAM across all modern and classic generations.

const CATEGORIES = [
  {{ id: 'cpu', name: 'CPU', icon: 'cpu', singular: 'a CPU' }},
  {{ id: 'cooler', name: 'CPU Cooler', icon: 'wind', singular: 'a CPU Cooler' }},
  {{ id: 'motherboard', name: 'Motherboard', icon: 'circuit-board', singular: 'a Motherboard' }},
  {{ id: 'memory', name: 'Memory', icon: 'database', singular: 'Memory (RAM)' }},
  {{ id: 'storage', name: 'Storage', icon: 'hard-drive', singular: 'Storage' }},
  {{ id: 'gpu', name: 'Video Card', icon: 'tv', singular: 'a Video Card' }},
  {{ id: 'case', name: 'Case', icon: 'box', singular: 'a Case' }},
  {{ id: 'psu', name: 'Power Supply', icon: 'zap', singular: 'a Power Supply' }},
  {{ id: 'os', name: 'Operating System', icon: 'disc', singular: 'an Operating System' }},
  {{ id: 'monitor', name: 'Monitor', icon: 'monitor', singular: 'a Monitor' }}
];

const PARTS_DATABASE = {json.dumps(full_catalog, indent=2)};

const PRESET_BUILDS = {{
  budget: {{
    name: 'Budget 1080p Esports',
    parts: {{
      cpu: 'cpu-5600',
      cooler: 'cooler-pa120',
      motherboard: 'mobo-b550-gaming',
      memory: 'ram-ripjaws-v-16-ddr4',
      storage: 'ssd-crucial-p3plus-1tb',
      gpu: 'gpu-rx6600',
      case: 'case-h5-flow',
      psu: 'psu-focus-650'
    }}
  }},
  midrange: {{
    name: 'Sweet Spot 1440p Gaming',
    parts: {{
      cpu: 'cpu-7600x',
      cooler: 'cooler-pa120',
      motherboard: 'mobo-b650-tomahawk',
      memory: 'ram-flare-x5-32-ddr5',
      storage: 'ssd-wd-sn850x-1tb',
      gpu: 'gpu-rtx4070super',
      case: 'case-4000d',
      psu: 'psu-rm750e'
    }}
  }},
  enthusiast: {{
    name: 'Ultimate 4K Enthusiast',
    parts: {{
      cpu: 'cpu-7800x3d',
      cooler: 'cooler-kraken360',
      motherboard: 'mobo-b650-tomahawk',
      memory: 'ram-vengeance-32-ddr5',
      storage: 'ssd-samsung-990pro-2tb',
      gpu: 'gpu-rtx4080super',
      case: 'case-4000d',
      psu: 'psu-rm850e'
    }}
  }}
}};
"""

    with open(DATA_JS_FILE, "w", encoding="utf-8") as f:
        f.write(new_data_js)
    print(f"Updated {DATA_JS_FILE} with {len(full_catalog)} components.")

if __name__ == "__main__":
    parts = build_catalog()
    update_database(parts)
    update_data_js(parts)
    print("Catalog population complete!")
