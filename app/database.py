"""
Database access layer using SQLite with schema migration and default seed data.
"""
from datetime import datetime
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = Path(__file__).resolve().parent.parent / "store.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_column(cursor: sqlite3.Cursor, table: str, column: str, col_def: str) -> None:
    cursor.execute(f"PRAGMA table_info({table});")
    existing_cols = {row["name"] for row in cursor.fetchall()}
    if column not in existing_cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def};")


def init_db() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL,
            stock INTEGER NOT NULL,
            badge TEXT,
            specs TEXT,
            image_url TEXT
        );
        """
    )
    _ensure_column(cursor, "products", "specs", "TEXT")
    _ensure_column(cursor, "products", "image_url", "TEXT")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            zip_code TEXT NOT NULL DEFAULT '80000-000',
            payment_method TEXT NOT NULL,
            subtotal_amount REAL NOT NULL DEFAULT 0.0,
            discount_amount REAL NOT NULL DEFAULT 0.0,
            shipping_cost REAL NOT NULL DEFAULT 0.0,
            coupon_code TEXT,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    _ensure_column(cursor, "orders", "zip_code", "TEXT NOT NULL DEFAULT '80000-000'")
    _ensure_column(cursor, "orders", "subtotal_amount", "REAL NOT NULL DEFAULT 0.0")
    _ensure_column(cursor, "orders", "discount_amount", "REAL NOT NULL DEFAULT 0.0")
    _ensure_column(cursor, "orders", "shipping_cost", "REAL NOT NULL DEFAULT 0.0")
    _ensure_column(cursor, "orders", "coupon_code", "TEXT")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coupons (
            code TEXT PRIMARY KEY,
            discount_percent REAL NOT NULL,
            free_shipping INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            author_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
        """
    )

    default_images = {
        "Teclado Mecanico TKL RGB": "/static/images/kb-tkl.jpg",
        "Mouse Ergonomico Vertical 4000 DPI": "/static/images/mouse-vertical.jpg",
        "Headset Wireless com Cancelamento Ativo": "/static/images/headset-anc.jpg",
        "Suporte Articulado a Gas para Monitor": "/static/images/monitor-arm.jpg",
        "Dock Station USB-C 10 em 1": "/static/images/dock-usbc.jpg",
        "Desk Mat Cordura 900x400mm": "/static/images/deskmat-cordura.jpg",
    }

    # Seed Products if empty
    cursor.execute("SELECT COUNT(*) as count FROM products;")
    row = cursor.fetchone()
    if row and row["count"] == 0:
        seed_products = [
            (
                "Teclado Mecanico TKL RGB",
                "Perifericos",
                349.90,
                "Switches Hot-swap lubrificados de fabrica, keycaps PBT double-shot e conectividade USB-C destacavel.",
                25,
                "Mais Vendido",
                "Formato: TKL (87 teclas) | Switch: Tactile Brown Lubed | Keycaps: PBT Double-Shot | Polling Rate: 1000Hz | Cabo: USB-C Trancado 1.8m",
                "/static/images/kb-tkl.jpg",
            ),
            (
                "Mouse Ergonomico Vertical 4000 DPI",
                "Perifericos",
                179.90,
                "Sensor optico de alta precisao, conexao dual (2.4GHz + Bluetooth 5.2) e pegada anatomica antifadiga.",
                40,
                "Destaque",
                "Angulo Vertical: 57 graus | Sensor: PixArt PAW3212 (ate 4000 DPI) | Bateria: 500mAh Recarregavel USB-C | Conexao: Dongle 2.4G + BT 5.2",
                "/static/images/mouse-vertical.jpg",
            ),
            (
                "Headset Wireless com Cancelamento Ativo",
                "Audio",
                489.00,
                "Drivers de neodimio de 50mm, bateria para 40 horas e microfone cardioide destacavel com cancelamento de ruido.",
                18,
                "Premium",
                "Drivers: 50mm Neodimio | ANC: Hibrido (-38dB) | Autonomia: 40h continuas | Latencia: 20ms Ultra-Low Dongle | Peso: 285g",
                "/static/images/headset-anc.jpg",
            ),
            (
                "Suporte Articulado a Gas para Monitor",
                "Setup",
                229.00,
                "Pistao a gas com ajuste micrometrico de altura, inclinacao 360 graus e padrao VESA 75/100 para telas ate 34 polegadas.",
                30,
                None,
                "Capacidade: 2kg a 9kg | Telas: 17\" a 34\" Ultrawide | VESA: 75x75 e 100x100mm | Fixacao: Morsa ou Furacao | Organizador de cabos integrado",
                "/static/images/monitor-arm.jpg",
            ),
            (
                "Dock Station USB-C 10 em 1",
                "Produtividade",
                289.00,
                "Chassi de aluminio com duas saidas HDMI 4K@60Hz, Gigabit Ethernet, leitor SD/TF e Power Delivery 100W.",
                15,
                "Novo",
                "Video: Dual HDMI 4K@60Hz | Rede: RJ45 Gigabit (1000Mbps) | Energia: USB-C PD 100W Pass-Through | Dados: 3x USB 3.0 (5Gbps) + SD/MicroSD",
                "/static/images/dock-usbc.jpg",
            ),
            (
                "Desk Mat Cordura 900x400mm",
                "Setup",
                99.00,
                "Superficie impermeavel em tecido militar Cordura, bordas com costura reforcada e base em borracha antiderrapante.",
                50,
                None,
                "Dimensoes: 900 x 400 x 4mm | Tecido: Cordura Balistica Impermeavel | Base: Borracha Natural Antiderrapante | Borda: Costura Low-Profile",
                "/static/images/deskmat-cordura.jpg",
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO products (name, category, price, description, stock, badge, specs, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            seed_products,
        )
    else:
        # Ensure existing products have specs and image_url populated
        default_specs = {
            "Teclado Mecanico TKL RGB": "Formato: TKL (87 teclas) | Switch: Tactile Brown Lubed | Keycaps: PBT Double-Shot | Polling Rate: 1000Hz",
            "Mouse Ergonomico Vertical 4000 DPI": "Angulo Vertical: 57 graus | Sensor: PixArt 4000 DPI | Bateria: Recarregavel USB-C | Conexao: 2.4G + BT 5.2",
            "Headset Wireless com Cancelamento Ativo": "Drivers: 50mm Neodimio | ANC: Hibrido (-38dB) | Autonomia: 40h | Latencia: 20ms Ultra-Low",
            "Suporte Articulado a Gas para Monitor": "Capacidade: 2kg a 9kg | Telas: 17\" a 34\" | VESA: 75x75 e 100x100mm | Fixacao: Morsa/Furacao",
            "Dock Station USB-C 10 em 1": "Video: Dual HDMI 4K@60Hz | Rede: RJ45 Gigabit | Energia: PD 100W | Dados: 3x USB 3.0 + SD/TF",
            "Desk Mat Cordura 900x400mm": "Dimensoes: 900 x 400 x 4mm | Tecido: Cordura Impermeavel | Base: Borracha Natural",
        }
        for p_name, spec_text in default_specs.items():
            cursor.execute(
                "UPDATE products SET specs = ? WHERE name = ? AND (specs IS NULL OR specs = '');",
                (spec_text, p_name),
            )
        for p_name, img_url in default_images.items():
            cursor.execute(
                "UPDATE products SET image_url = ? WHERE name = ? AND (image_url IS NULL OR image_url = '');",
                (img_url, p_name),
            )

    # Seed Coupons if empty
    cursor.execute("SELECT COUNT(*) as count FROM coupons;")
    c_row = cursor.fetchone()
    if c_row and c_row["count"] == 0:
        seed_coupons = [
            ("DEV10", 10.0, 0, 1),
            ("SIDI20", 20.0, 1, 1),
            ("FRETEGRATIS", 0.0, 1, 1),
        ]
        cursor.executemany(
            """
            INSERT INTO coupons (code, discount_percent, free_shipping, active)
            VALUES (?, ?, ?, ?);
            """,
            seed_coupons,
        )

    # Seed Reviews if empty
    cursor.execute("SELECT COUNT(*) as count FROM reviews;")
    r_row = cursor.fetchone()
    if r_row and r_row["count"] == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        seed_reviews = [
            (1, "Lucas M.", 5, "Tactile feedback impecavel para sessoes longas no Neovim. Zero rattle nos estabilizadores.", now_str),
            (1, "Rafael S.", 5, "Construcao solida e keycaps PBT nao ficam brilhando com o tempo.", now_str),
            (2, "Marina K.", 5, "Eliminou minha dor no punho em 3 dias de uso. Alternar entre o PC e o MacBook via botao e instantaneo.", now_str),
            (3, "Andre V.", 4, "Cancelamento de ruido bloqueia totalmente o barulho de ar-condicionado. Microfone muito limpo para dailies.", now_str),
            (4, "Carlos T.", 5, "Segura meu ultrawide de 34 polegadas sem ceder um milimetro.", now_str),
            (5, "Guilherme W.", 5, "Dois monitores 4K a 60Hz rodando estaveis com um unico cabo USB-C e alimentando o notebook.", now_str),
            (6, "Beatriz L.", 5, "Deslize rapido do mouse e realmente repele liquidos.", now_str),
        ]
        cursor.executemany(
            """
            INSERT INTO reviews (product_id, author_name, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?);
            """,
            seed_reviews,
        )

    conn.commit()
    conn.close()


def get_all_products(category: Optional[str] = None, sort_by: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT
            p.*,
            COALESCE(ROUND(AVG(r.rating), 1), 0.0) AS avg_rating,
            COUNT(r.id) AS review_count
        FROM products p
        LEFT JOIN reviews r ON r.product_id = p.id
    """
    params: List[Any] = []
    if category and category.lower() != "todos":
        base_query += " WHERE p.category = ?"
        params.append(category)

    base_query += " GROUP BY p.id"

    order_map = {
        "price_asc": "p.price ASC",
        "price_desc": "p.price DESC",
        "rating_desc": "avg_rating DESC, review_count DESC",
        "name_asc": "p.name ASC",
        "stock_desc": "p.stock DESC",
    }
    order_clause = order_map.get(sort_by or "", "p.id ASC")
    base_query += f" ORDER BY {order_clause}"

    cursor.execute(base_query, tuple(params))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            p.*,
            COALESCE(ROUND(AVG(r.rating), 1), 0.0) AS avg_rating,
            COUNT(r.id) AS review_count
        FROM products p
        LEFT JOIN reviews r ON r.product_id = p.id
        WHERE p.id = ?
        GROUP BY p.id
        """,
        (product_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_categories() -> List[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row["category"] for row in rows]


def get_product_reviews(product_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM reviews WHERE product_id = ? ORDER BY id DESC",
        (product_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_product_review(product_id: int, author_name: str, rating: int, comment: str) -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO reviews (product_id, author_name, rating, comment, created_at)
        VALUES (?, ?, ?, ?, ?);
        """,
        (product_id, author_name, rating, comment, created_at),
    )
    review_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {
        "id": int(review_id or 0),
        "product_id": product_id,
        "author_name": author_name,
        "rating": rating,
        "comment": comment,
        "created_at": created_at,
    }


def get_coupon(code: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coupons WHERE UPPER(code) = UPPER(?)", (code.strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["free_shipping"] = bool(d["free_shipping"])
    d["active"] = bool(d["active"])
    return d


def get_all_coupons() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM coupons ORDER BY code ASC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d["free_shipping"] = bool(d["free_shipping"])
        d["active"] = bool(d["active"])
        result.append(d)
    return result


def upsert_coupon(code: str, discount_percent: float, free_shipping: bool, active: bool = True) -> Dict[str, Any]:
    clean_code = code.strip().upper()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO coupons (code, discount_percent, free_shipping, active)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(code) DO UPDATE SET
            discount_percent = excluded.discount_percent,
            free_shipping = excluded.free_shipping,
            active = excluded.active;
        """,
        (clean_code, discount_percent, int(free_shipping), int(active)),
    )
    conn.commit()
    conn.close()
    return {
        "code": clean_code,
        "discount_percent": discount_percent,
        "free_shipping": free_shipping,
        "active": active,
    }


def calculate_shipping(zip_code: str, subtotal: float, free_shipping_coupon: bool = False) -> Tuple[str, float, int, bool]:
    """
    Calculates shipping region, cost, estimated days, and whether free shipping was applied.
    Free shipping threshold: R$ 500.00 or active free_shipping coupon.
    """
    digits = "".join(ch for ch in zip_code if ch.isdigit())
    first_digit = digits[0] if digits else "8"

    region_table: Dict[str, Tuple[str, float, int]] = {
        "8": ("Sul (PR/SC)", 18.90, 2),
        "9": ("Sul (RS)", 22.90, 3),
        "0": ("Sudeste (SP Capital)", 19.90, 2),
        "1": ("Sudeste (SP Interior)", 21.90, 3),
        "2": ("Sudeste (RJ/ES)", 24.90, 4),
        "3": ("Sudeste (MG)", 24.90, 4),
        "7": ("Centro-Oeste", 29.90, 5),
        "4": ("Nordeste (BA/SE)", 34.90, 6),
        "5": ("Nordeste (PE/AL/PB/RN)", 36.90, 7),
        "6": ("Norte / Nordeste", 42.90, 8),
    }
    region, base_cost, days = region_table.get(first_digit, ("Nacional Padrao", 27.90, 5))

    if subtotal >= 500.0 or free_shipping_coupon:
        return region, 0.0, days, True
    return region, base_cost, days, False
