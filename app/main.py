"""
FastAPI application core for the store.
"""
from datetime import datetime
from pathlib import Path
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import get_all_products, get_categories, get_db_connection, get_product_by_id, init_db
from .models import CheckoutRequest, OrderItemResponse, OrderResponse, ProductSchema

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="NovaStore API",
    description="Engine e API da loja virtual de desenvolvimento",
    version="1.0.0",
)

# Static and Templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index_page(request: Request) -> HTMLResponse:
    categories = get_categories()
    products = get_all_products()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "categories": categories,
            "products": products,
        },
    )


@app.get("/order/{order_id}", response_class=HTMLResponse)
def order_page(request: Request, order_id: str) -> HTMLResponse:
    order = get_order_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    return templates.TemplateResponse(
        request=request,
        name="order_success.html",
        context={
            "order": order,
        },
    )


@app.get("/api/products", response_model=List[ProductSchema])
def list_products(category: Optional[str] = Query(None)) -> List[ProductSchema]:
    raw_products = get_all_products(category)
    return [ProductSchema(**p) for p in raw_products]


@app.get("/api/categories", response_model=List[str])
def list_categories() -> List[str]:
    return get_categories()


@app.post("/api/checkout", response_model=OrderResponse)
def create_order(payload: CheckoutRequest) -> OrderResponse:
    conn = get_db_connection()
    cursor = conn.cursor()

    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    order_items: List[OrderItemResponse] = []
    total_amount = 0.0

    try:
        # Validate stock and calculate items
        for item in payload.items:
            product = get_product_by_id(item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Produto ID {item.product_id} nao encontrado.")
            if product["stock"] < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente para '{product['name']}'. Disponivel: {product['stock']}.",
                )

            subtotal = round(product["price"] * item.quantity, 2)
            total_amount += subtotal

            order_items.append(
                OrderItemResponse(
                    product_id=product["id"],
                    product_name=product["name"],
                    quantity=item.quantity,
                    unit_price=product["price"],
                    subtotal=subtotal,
                )
            )

        total_amount = round(total_amount, 2)

        # Insert Order
        cursor.execute(
            """
            INSERT INTO orders (id, customer_name, customer_email, customer_address, payment_method, total_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                order_id,
                payload.customer_name,
                payload.customer_email,
                payload.customer_address,
                payload.payment_method,
                total_amount,
                "Confirmado",
                created_at,
            ),
        )

        # Insert Items & update stock
        for oi in order_items:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (order_id, oi.product_id, oi.product_name, oi.quantity, oi.unit_price, oi.subtotal),
            )
            cursor.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?;",
                (oi.quantity, oi.product_id),
            )

        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erro no processamento do pedido: {str(e)}")
    finally:
        conn.close()

    return OrderResponse(
        order_id=order_id,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        customer_address=payload.customer_address,
        payment_method=payload.payment_method,
        total_amount=total_amount,
        status="Confirmado",
        created_at=created_at,
        items=order_items,
    )


@app.get("/api/orders/{order_id}", response_model=OrderResponse)
def get_order_endpoint(order_id: str) -> OrderResponse:
    order = get_order_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    return order


def get_order_details(order_id: str) -> Optional[OrderResponse]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        return None

    cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    item_rows = cursor.fetchall()
    conn.close()

    items = [
        OrderItemResponse(
            product_id=r["product_id"],
            product_name=r["product_name"],
            quantity=r["quantity"],
            unit_price=r["unit_price"],
            subtotal=r["subtotal"],
        )
        for r in item_rows
    ]

    return OrderResponse(
        order_id=order_row["id"],
        customer_name=order_row["customer_name"],
        customer_email=order_row["customer_email"],
        customer_address=order_row["customer_address"],
        payment_method=order_row["payment_method"],
        total_amount=order_row["total_amount"],
        status=order_row["status"],
        created_at=order_row["created_at"],
        items=items,
    )
