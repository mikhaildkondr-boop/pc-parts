"""
PickMyPC REST API Backend
Powered by Python standard library & SQLite3.
Zero external dependencies required.
"""

import http.server
import socketserver
import sqlite3
import json
import urllib.parse
import os
import uuid

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "pcparts.db")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

class APIRouter(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for frontend integration
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def send_json(self, data, status=200):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def send_error_json(self, message, status=400):
        self.send_json({"error": message}, status=status)

    def parse_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_data = self.rfile.read(content_length)
            try:
                return json.loads(raw_data.decode("utf-8"))
            except Exception:
                return None
        return {}

    # =========================================================================
    # GET Handlers
    # =========================================================================
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/")
        query = urllib.parse.parse_qs(parsed_url.query)

        # 1. API System Status
        if path == "/api/status":
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT count(*) FROM parts")
                parts_count = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM builds")
                builds_count = cur.fetchone()[0]
                return self.send_json({
                    "status": "online",
                    "sqlite_version": sqlite3.sqlite_version,
                    "database": "pcparts.db",
                    "total_parts": parts_count,
                    "total_builds": builds_count
                })

        # 2. Get Countries Configuration
        if path == "/api/countries":
            import country_pricing
            return self.send_json(list(country_pricing.COUNTRIES.values()))

        # 3. Get Categories Summary
        if path == "/api/categories":
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT category, count(*) as count FROM parts GROUP BY category")
                rows = cur.fetchall()
                result = [{"category": r["category"], "count": r["count"]} for r in rows]
                return self.send_json(result)

        # 4. Get Parts List (with filtering, country pricing, and condition)
        if path == "/api/parts":
            category = query.get("category", [None])[0]
            brand = query.get("brand", [None])[0]
            search = query.get("search", [None])[0]
            max_price = query.get("maxPrice", [None])[0]
            sort = query.get("sort", ["name_asc"])[0]
            country = query.get("country", ["US"])[0].upper()
            condition = query.get("condition", ["any"])[0].lower()
            if country not in ["US", "UA", "IT", "DE", "GB", "FR", "ES", "EU"]:
                country = "US"

            sql = """
                SELECT p.*, 
                       cp.price as localized_price, 
                       cp.currency as localized_currency, 
                       cp.merchant as localized_merchant, 
                       cp.shipping_info as localized_shipping,
                       cp.used_price,
                       cp.used_merchant,
                       cp.used_shipping_info,
                       cp.used_savings,
                       cp.used_savings_pct
                FROM parts p
                LEFT JOIN country_prices cp ON p.id = cp.part_id AND cp.country_code = ?
                WHERE 1=1
            """
            params = [country]

            if category:
                sql += " AND p.category = ?"
                params.append(category)
            if brand:
                sql += " AND p.brand LIKE ?"
                params.append(f"%{brand}%")
            if search:
                sql += " AND (p.name LIKE ? OR p.brand LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])
            if max_price:
                try:
                    price_col = "cp.used_price" if condition == "used" else "COALESCE(cp.price, p.price)"
                    sql += f" AND {price_col} <= ?"
                    params.append(float(max_price))
                except ValueError:
                    pass

            # Ordering
            price_sort_col = "cp.used_price" if condition == "used" else "COALESCE(cp.price, p.price)"
            if sort == "price_asc":
                sql += f" ORDER BY {price_sort_col} ASC"
            elif sort == "price_desc":
                sql += f" ORDER BY {price_sort_col} DESC"
            elif sort == "rating_desc":
                sql += " ORDER BY p.rating DESC"
            else:
                sql += " ORDER BY p.name ASC"

            with get_db() as conn:
                cur = conn.cursor()
                cur.execute(sql, params)
                rows = cur.fetchall()

                parts = []
                for r in rows:
                    p = dict(r)
                    new_price = p.get("localized_price") if p.get("localized_price") is not None else p["price"]
                    curr = p.get("localized_currency") or "USD"
                    new_merch = p.get("localized_merchant") or p["merchant"]
                    new_ship = p.get("localized_shipping") or "FREE Shipping"

                    used_price = p.get("used_price")
                    used_merch = p.get("used_merchant")
                    used_ship = p.get("used_shipping_info")
                    used_savings = p.get("used_savings") or 0.0
                    used_savings_pct = p.get("used_savings_pct") or 0

                    if condition == "used" and used_price is not None:
                        p["price"] = used_price
                        p["merchant"] = used_merch
                        p["shipping"] = used_ship
                        p["condition"] = "used"
                    else:
                        p["price"] = new_price
                        p["merchant"] = new_merch
                        p["shipping"] = new_ship
                        p["condition"] = "new"

                    p["currency"] = curr
                    p["used_price"] = used_price
                    p["used_merchant"] = used_merch
                    p["used_shipping"] = used_ship
                    p["used_savings"] = used_savings
                    p["used_savings_pct"] = used_savings_pct

                    p.pop("localized_price", None)
                    p.pop("localized_currency", None)
                    p.pop("localized_merchant", None)
                    p.pop("localized_shipping", None)
                    p.pop("used_shipping_info", None)

                    try:
                        p["specs"] = json.loads(p["specs"])
                    except Exception:
                        pass
                    parts.append(p)

                return self.send_json(parts)

        # 5. Get Single Part by ID
        if path.startswith("/api/parts/"):
            part_id = path.replace("/api/parts/", "")
            country = query.get("country", ["US"])[0].upper()
            condition = query.get("condition", ["new"])[0].lower()

            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM parts WHERE id = ?", (part_id,))
                row = cur.fetchone()
                if not row:
                    return self.send_error_json(f"Part with ID '{part_id}' not found", 404)

                part = dict(row)
                try:
                    part["specs"] = json.loads(part["specs"])
                except Exception:
                    pass

                # Fetch all country prices with used details
                cur.execute("""
                    SELECT country_code, currency, price, merchant, shipping_info,
                           used_price, used_merchant, used_shipping_info, used_savings, used_savings_pct
                    FROM country_prices WHERE part_id = ?
                """, (part_id,))
                cp_rows = cur.fetchall()
                part["country_prices"] = {
                    r["country_code"]: {
                        "currency": r["currency"],
                        "price": r["price"],
                        "merchant": r["merchant"],
                        "shipping": r["shipping_info"],
                        "used_price": r["used_price"],
                        "used_merchant": r["used_merchant"],
                        "used_shipping": r["used_shipping_info"],
                        "used_savings": r["used_savings"],
                        "used_savings_pct": r["used_savings_pct"]
                    } for r in cp_rows
                }

                # Apply localized fields if requested
                if country in part["country_prices"]:
                    loc = part["country_prices"][country]
                    if condition == "used":
                        part["price"] = loc["used_price"]
                        part["merchant"] = loc["used_merchant"]
                        part["shipping"] = loc["used_shipping"]
                        part["condition"] = "used"
                    else:
                        part["price"] = loc["price"]
                        part["merchant"] = loc["merchant"]
                        part["shipping"] = loc["shipping"]
                        part["condition"] = "new"

                    part["currency"] = loc["currency"]
                    part["used_price"] = loc["used_price"]
                    part["used_merchant"] = loc["used_merchant"]
                    part["used_shipping"] = loc["used_shipping"]
                    part["used_savings"] = loc["used_savings"]
                    part["used_savings_pct"] = loc["used_savings_pct"]

                return self.send_json(part)

        # 5. Get Saved Builds List
        if path == "/api/builds":
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM builds ORDER BY created_at DESC")
                rows = cur.fetchall()
                builds = []
                for r in rows:
                    b = dict(r)
                    try:
                        b["parts_data"] = json.loads(b["parts_data"])
                    except Exception:
                        pass
                    builds.append(b)
                return self.send_json(builds)

        # 6. Get Single Build by ID
        if path.startswith("/api/builds/"):
            build_id = path.replace("/api/builds/", "")
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("SELECT * FROM builds WHERE id = ?", (build_id,))
                row = cur.fetchone()
                if not row:
                    return self.send_error_json(f"Build with ID '{build_id}' not found", 404)

                build = dict(row)
                try:
                    build["parts_data"] = json.loads(build["parts_data"])
                except Exception:
                    pass
                return self.send_json(build)

        # Default static file fallback
        super().do_GET()

    # =========================================================================
    # POST Handlers
    # =========================================================================
    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/")
        body = self.parse_body()

        if body is None:
            return self.send_error_json("Invalid JSON payload", 400)

        # 1. Create / Save a PC Build
        if path == "/api/builds":
            title = body.get("title", "Custom PC Build")
            description = body.get("description", "")
            total_price = float(body.get("total_price", 0.0))
            estimated_wattage = int(body.get("estimated_wattage", 0))
            parts_data = body.get("parts_data", {})

            build_id = f"build-{uuid.uuid4().hex[:8]}"

            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO builds (id, title, description, total_price, estimated_wattage, parts_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    build_id,
                    title,
                    description,
                    total_price,
                    estimated_wattage,
                    json.dumps(parts_data)
                ))
                conn.commit()

            return self.send_json({
                "message": "Build saved successfully to SQLite database.",
                "id": build_id,
                "title": title,
                "total_price": total_price
            }, status=201)

        # 2. Add New Hardware Part
        if path == "/api/parts":
            required = ["id", "category", "name", "brand", "price"]
            for field in required:
                if field not in body:
                    return self.send_error_json(f"Missing required field: '{field}'", 400)

            part_id = body["id"]
            category = body["category"]
            name = body["name"]
            brand = body["brand"]
            price = float(body["price"])
            merchant = body.get("merchant", "Custom Merchant")
            rating = float(body.get("rating", 5.0))
            reviews = int(body.get("reviews", 1))
            specs = body.get("specs", {})

            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT OR REPLACE INTO parts (id, category, name, brand, price, merchant, rating, reviews, specs)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    part_id, category, name, brand, price, merchant, rating, reviews, json.dumps(specs)
                ))
                conn.commit()

            return self.send_json({
                "message": f"Part '{name}' stored successfully in SQLite.",
                "id": part_id
            }, status=201)

        return self.send_error_json("Endpoint not found", 404)

    # =========================================================================
    # DELETE Handlers
    # =========================================================================
    def do_DELETE(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/")

        # Delete a Build
        if path.startswith("/api/builds/"):
            build_id = path.replace("/api/builds/", "")
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM builds WHERE id = ?", (build_id,))
                conn.commit()
                if cur.rowcount == 0:
                    return self.send_error_json("Build not found", 404)
                return self.send_json({"message": f"Build '{build_id}' deleted."})

        # Delete a Part
        if path.startswith("/api/parts/"):
            part_id = path.replace("/api/parts/", "")
            with get_db() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM parts WHERE id = ?", (part_id,))
                conn.commit()
                if cur.rowcount == 0:
                    return self.send_error_json("Part not found", 404)
                return self.send_json({"message": f"Part '{part_id}' deleted."})

        return self.send_error_json("Endpoint not found", 404)

def run_server():
    # Make sure DB exists
    if not os.path.exists(DB_FILE):
        import init_db
        conn = init_db.init_db()
        init_db.seed_parts(conn)
        conn.close()

    server_address = ("", PORT)
    with socketserver.TCPServer(server_address, APIRouter) as httpd:
        print(f"=================================================")
        print(f" PickMyPC Backend Server (SQLite3)")
        print(f" Database File: {DB_FILE}")
        print(f" Listening on port {PORT}...")
        print(f" Endpoints:")
        print(f"   - GET  /api/status")
        print(f"   - GET  /api/parts")
        print(f"   - GET  /api/parts/<id>")
        print(f"   - POST /api/parts")
        print(f"   - GET  /api/builds")
        print(f"   - POST /api/builds")
        print(f"=================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")

if __name__ == "__main__":
    run_server()
