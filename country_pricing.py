"""
Country Pricing & Used Hardware Engine for PickMyPC
Supports:
  - Ukraine (UA) - UAH (₴) [Rozetka, Telemart, Brain, ITbox, Comfy] & Used: [OLX.ua, Overclockers.ua Барахолка, Telemart Outlet]
  - Italy (IT) - EUR (€) [Amazon.it, Drako.it, BPM-Power, ePRICE] & Used: [Subito.it, eBay.it Usato, Amazon Seconda Mano]
  - United States (US) - USD ($) [Amazon, Newegg, Best Buy, Micro Center] & Used: [eBay Pre-Owned, r/hardwareswap, Jawa.gg]
  - Germany (DE) - EUR (€) [Mindfactory, Caseking, Alternate.de] & Used: [Kleinanzeigen, ComputerBase Marktplatz, Alternate Outlet]
  - United Kingdom (GB) - GBP (£) [Overclockers UK, Scan Computers, Amazon UK] & Used: [eBay UK, CeX, Overclockers B-Grade]
  - France (FR) - EUR (€) [LDLC, TopAchat, Amazon.fr] & Used: [Leboncoin, LDLC Coin des Affaires, eBay.fr]
  - Spain (ES) - EUR (€) [PcComponentes, Coolmod, Amazon.es] & Used: [Wallapop, PcComponentes Reacondicionados, Milanuncios]
  - Europe (EU) - EUR (€) [Caseking, Amazon EU, Computer Universe] & Used: [eBay Europe Refurbished, Caseking B-Ware]

Strict Exclusion: Russia is NOT included.
"""

import math
import hashlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Country metadata dictionary
COUNTRIES = {
    "US": {
        "code": "US",
        "name": "United States",
        "flag": "🇺🇸",
        "currency": "USD",
        "symbol": "$",
        "position": "prefix",
        "rate": 1.0,
        "taxMultiplier": 1.0,
        "merchants": ["Amazon", "Newegg", "Best Buy", "Micro Center", "B&H"],
        "defaultShipping": "FREE Shipping",
        "marketNote": "US MSRP / Street prices (excl. sales tax)",
        "usedMerchants": ["eBay (Pre-Owned)", "r/hardwareswap", "Jawa.gg", "Micro Center Open Box", "Amazon Renewed"],
        "usedShipping": ["eBay Money Back Guarantee", "USPS Priority Insured", "Micro Center 90-Day Warranty", "PayPal Goods & Services Protected"]
    },
    "UA": {
        "code": "UA",
        "name": "Ukraine",
        "flag": "🇺🇦",
        "currency": "UAH",
        "symbol": "₴",
        "position": "suffix",
        "rate": 41.5,
        "taxMultiplier": 1.18,
        "merchants": ["Telemart", "Rozetka", "Brain", "ITbox", "Comfy", "Moyo"],
        "defaultShipping": "Безкоштовна доставка",
        "shippingOptions": ["Безкоштовна доставка", "Самовивіз із точки видачі", "Оплата частинами 0%"],
        "marketNote": "Реальні ціни в Україні (Rozetka, Telemart, Brain, з урахуванням ПДВ 20%)",
        "usedMerchants": ["OLX.ua", "Overclockers.ua (Барахолка)", "Telemart Outlet (Б/В)", "Rozetka Маркетплейс Б/В", "e-Katalog Б/В"],
        "usedShipping": ["OLX Доставка (Нова Пошта)", "Самовивіз із перевіркою", "Гарантія 3 міс. (Outlet)", "Накладений платіж"]
    },
    "IT": {
        "code": "IT",
        "name": "Italy",
        "flag": "🇮🇹",
        "currency": "EUR",
        "symbol": "€",
        "position": "prefix",
        "rate": 0.92,
        "taxMultiplier": 1.16,
        "merchants": ["Amazon.it", "Drako.it", "BPM-Power", "ePRICE", "NextHS", "AK Informatica"],
        "defaultShipping": "Spedizione Prime gratuita",
        "shippingOptions": ["Spedizione Prime gratuita", "Spedizione 24/48h", "Spedizione inclusa"],
        "marketNote": "Prezzi reali in Italia (Amazon.it, Drako.it, BPM-Power, IVA 22% inclusa)",
        "usedMerchants": ["Subito.it", "eBay.it (Usato Garantito)", "Amazon Seconda Mano (Warehouse)", "Vinted Tech", "Wallapop IT"],
        "usedShipping": ["TuttoSubito Spedizione Protetta", "Garanzia Cliente eBay", "Spedizione Tracciata 24/48h", "Reso 30 giorni Amazon"]
    },
    "DE": {
        "code": "DE",
        "name": "Germany",
        "flag": "🇩🇪",
        "currency": "EUR",
        "symbol": "€",
        "position": "prefix",
        "rate": 0.92,
        "taxMultiplier": 1.12,
        "merchants": ["Mindfactory", "Caseking", "Alternate.de", "Amazon.de", "Notebooksbilliger"],
        "defaultShipping": "Kostenloser Versand",
        "shippingOptions": ["Kostenloser Versand", "MindStar Sonderpreis", "Abholung im Store"],
        "marketNote": "Preise in Deutschland (Mindfactory, Caseking, Alternate, 19% MwSt. inkl.)",
        "usedMerchants": ["Kleinanzeigen (Gebraucht)", "ComputerBase Marktplatz", "Alternate Outlet (B-Ware)", "Mindfactory B-Ware"],
        "usedShipping": ["Sicher bezahlen Käuferschutz", "DHL Versichert", "12 Monate Händlergarantie", "Abholung & Funktionstest"]
    },
    "GB": {
        "code": "GB",
        "name": "United Kingdom",
        "flag": "🇬🇧",
        "currency": "GBP",
        "symbol": "£",
        "position": "prefix",
        "rate": 0.77,
        "taxMultiplier": 1.15,
        "merchants": ["Overclockers UK", "Scan Computers", "Amazon UK", "Ebuyer", "AWD-IT"],
        "defaultShipping": "Free UK Delivery",
        "shippingOptions": ["Free UK Delivery", "DPD Next Day Tracked", "Scan 3XS Guaranteed"],
        "marketNote": "UK retail pricing (Overclockers UK, Scan, 20% VAT included)",
        "usedMerchants": ["eBay UK (Used)", "CeX (webuy.com)", "Overclockers UK B-Grade", "Gumtree Tech"],
        "usedShipping": ["CeX 24-Month Warranty", "Royal Mail Tracked 24", "eBay Money Back Guarantee", "DPD Next Day"]
    },
    "FR": {
        "code": "FR",
        "name": "France",
        "flag": "🇫🇷",
        "currency": "EUR",
        "symbol": "€",
        "position": "prefix",
        "rate": 0.92,
        "taxMultiplier": 1.15,
        "merchants": ["LDLC", "TopAchat", "Amazon.fr", "Materiel.net"],
        "defaultShipping": "Livraison gratuite",
        "shippingOptions": ["Livraison gratuite", "Expédié sous 24h", "Retrait boutique LDLC"],
        "marketNote": "Prix en France (LDLC, TopAchat, Amazon.fr, TVA 20% incluse)",
        "usedMerchants": ["Leboncoin (Occasion)", "LDLC Coin des Affaires", "eBay.fr Occasion", "Vinted Tech France"],
        "usedShipping": ["Livraison Leboncoin Sécurisée", "Garantie LDLC 6 mois", "Colissimo Suivi", "Paiement Sécurisé"]
    },
    "ES": {
        "code": "ES",
        "name": "Spain",
        "flag": "🇪🇸",
        "currency": "EUR",
        "symbol": "€",
        "position": "prefix",
        "rate": 0.92,
        "taxMultiplier": 1.14,
        "merchants": ["PcComponentes", "Coolmod", "Amazon.es"],
        "defaultShipping": "Envío gratis 24h",
        "shippingOptions": ["Envío gratis 24h", "Garantía de sustitución", "Recogida PcComponentes"],
        "marketNote": "Precios en España (PcComponentes, Coolmod, IVA 21% incluido)",
        "usedMerchants": ["Wallapop (Segunda Mano)", "PcComponentes Reacondicionados", "Milanuncios Tech"],
        "usedShipping": ["Wallapop Envíos Protegido", "Garantía PcComponentes 1 año", "Puntopack Segura", "Prueba in situ"]
    },
    "EU": {
        "code": "EU",
        "name": "Europe (Pan-EU)",
        "flag": "🇪🇺",
        "currency": "EUR",
        "symbol": "€",
        "position": "prefix",
        "rate": 0.92,
        "taxMultiplier": 1.14,
        "merchants": ["Caseking", "Amazon EU", "Computer Universe"],
        "defaultShipping": "Free EU Shipping",
        "shippingOptions": ["Free EU Shipping", "EU Express Delivery", "Standard EU Shipping"],
        "marketNote": "Pan-European hardware benchmark pricing (EUR, EU VAT included)",
        "usedMerchants": ["eBay Europe Refurbished", "Caseking B-Ware", "Refurbed.com EU"],
        "usedShipping": ["EU Insured Delivery", "Buyer Protection Guaranteed", "1 Year Certified Refurbished"]
    }
}

def calculate_localized_price(base_usd_price, country_code, part_id="", condition="new"):
    """
    Computes a realistic local price (new or used) and assigns an authentic retailer/marketplace.
    """
    if country_code not in COUNTRIES:
        country_code = "US"
    
    cfg = COUNTRIES[country_code]
    
    seed_str = f"{part_id}_{country_code}_{condition}"
    h = int(hashlib.md5(seed_str.encode("utf-8")).hexdigest(), 16)
    
    variance_pct = ((h % 50) - 25) / 1000.0
    
    if condition == "used":
        # Used hardware discount factor typically 26% to 42% depending on component
        discount_base = 0.32 + (((h >> 3) % 15) - 7) / 100.0  # 25% - 39% discount
        used_multiplier = max(0.55, min(0.78, 1.0 - discount_base))
        raw_val = base_usd_price * cfg["rate"] * cfg["taxMultiplier"] * used_multiplier * (1.0 + variance_pct)
        merchants = cfg.get("usedMerchants", cfg["merchants"])
        shipping_opts = cfg.get("usedShipping", [cfg["defaultShipping"]])
    else:
        raw_val = base_usd_price * cfg["rate"] * cfg["taxMultiplier"] * (1.0 + variance_pct)
        merchants = cfg["merchants"]
        shipping_opts = cfg.get("shippingOptions", [cfg["defaultShipping"]])
    
    if cfg["currency"] == "UAH":
        val = round(raw_val)
        if val > 15000:
            val = (val // 100) * 100 - 1
        elif val > 3000:
            val = (val // 50) * 50 - 1
        elif val > 1000:
            val = (val // 10) * 10 - 1
        else:
            val = max(149, round(val / 10) * 10 - 1)
        final_price = float(val)
    elif cfg["currency"] == "EUR":
        endings = [0.90, 0.99, 0.95, 0.00]
        chosen_ending = endings[h % len(endings)]
        val = math.floor(raw_val) + chosen_ending
        final_price = round(val, 2)
    elif cfg["currency"] == "GBP":
        endings = [0.99, 0.95, 0.49, 0.00]
        chosen_ending = endings[h % len(endings)]
        val = math.floor(raw_val) + chosen_ending
        final_price = round(val, 2)
    else: # USD
        if condition == "used":
            final_price = round(raw_val, 2)
        else:
            final_price = round(base_usd_price, 2)
    
    merchant = merchants[h % len(merchants)]
    shipping = shipping_opts[(h >> 4) % len(shipping_opts)]
    
    return {
        "price": final_price,
        "currency": cfg["currency"],
        "symbol": cfg["symbol"],
        "merchant": merchant,
        "shipping": shipping,
        "condition": condition
    }

def generate_all_country_prices(base_usd_price, part_id=""):
    """
    Returns a dict mapping country code to localized new & used price and merchant info.
    """
    result = {}
    for ccode in COUNTRIES:
        new_data = calculate_localized_price(base_usd_price, ccode, part_id, condition="new")
        used_data = calculate_localized_price(base_usd_price, ccode, part_id, condition="used")
        
        # Calculate savings
        savings_amount = round(max(0, new_data["price"] - used_data["price"]), 2)
        savings_pct = round((savings_amount / new_data["price"] * 100.0) if new_data["price"] > 0 else 0)
        
        result[ccode] = {
            "price": new_data["price"],
            "currency": new_data["currency"],
            "symbol": new_data["symbol"],
            "merchant": new_data["merchant"],
            "shipping": new_data["shipping"],
            "condition": "new",
            "used_price": used_data["price"],
            "used_merchant": used_data["merchant"],
            "used_shipping": used_data["shipping"],
            "used_savings": savings_amount,
            "used_savings_pct": savings_pct
        }
    return result

if __name__ == "__main__":
    test_parts = [
        ("cpu-7800x3d", 439.00),
        ("gpu-rtx4070super", 599.00),
        ("cpu-3600", 95.00),
        ("gpu-gtx1660super", 199.00),
    ]
    for pid, price in test_parts:
        print(f"\n--- {pid} (Base ${price}) ---")
        prices = generate_all_country_prices(price, pid)
        for ccode in ["US", "UA", "IT", "DE"]:
            d = prices[ccode]
            print(f"  {COUNTRIES[ccode]['flag']} {ccode}:")
            print(f"     NEW : {d['price']} {d['currency']} @ {d['merchant']} ({d['shipping']})")
            print(f"     USED: {d['used_price']} {d['currency']} @ {d['used_merchant']} (Save {d['used_savings_pct']}%)")
