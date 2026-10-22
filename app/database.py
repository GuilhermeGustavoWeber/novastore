"""
Database access layer using SQLite with schema migration and default seed data.
"""
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "store.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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
            badge TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

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

    # Check if products already exist
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
            ),
            (
                "Mouse Ergonomico Vertical 4000 DPI",
                "Perifericos",
                179.90,
                "Sensor optico de alta precisao, conexao dual (2.4GHz + Bluetooth 5.2) e pegada anatomica antifadiga.",
                40,
                "Destaque",
            ),
            (
                "Headset Wireless com Cancelamento Ativo",
                "Audio",
                489.00,
                "Drivers de neodimio de 50mm, bateria para 40 horas e microfone cardioide destacavel com cancelamento de ruido.",
                18,
                "Premium",
            ),
            (
                "Suporte Articulado a Gas para Monitor",
                "Setup",
                229.00,
                "Pistao a gas com ajuste micrometrico de altura, inclinacao 360 graus e padrao VESA 75/100 para telas ate 34 polegadas.",
                30,
                None,
            ),
            (
                "Dock Station USB-C 10 em 1",
                "Produtividade",
                289.00,
                "Chassi de aluminio com duas saidas HDMI 4K@60Hz, Gigabit Ethernet, leitor SD/TF e Power Delivery 100W.",
                15,
                "Novo",
            ),
            (
                "Desk Mat Cordura 900x400mm",
                "Setup",
                99.00,
                "Superficie impermeavel em tecido militar Cordura, bordas com costura reforçada e base em borracha antiderrapante.",
                50,
                None,
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO products (name, category, price, description, stock, badge)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            seed_products,
        )

    conn.commit()
    conn.close()


def get_all_products(category: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    if category and category.lower() != "todos":
        cursor.execute("SELECT * FROM products WHERE category = ? ORDER BY id ASC", (category,))
    else:
        cursor.execute("SELECT * FROM products ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
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
