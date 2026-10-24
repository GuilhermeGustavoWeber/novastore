"""
End-to-end integration test suite covering the 4 evolution fronts of NovaStore v2.0.
"""
import unittest
from fastapi.testclient import TestClient

from app.main import app


class NovaStoreEvolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_01_catalog_sorting_and_reviews(self) -> None:
        # 1. List products sorted by price ascending
        res = self.client.get("/api/products?sort=price_asc")
        self.assertEqual(res.status_code, 200)
        products = res.json()
        self.assertGreaterEqual(len(products), 6)
        prices = [p["price"] for p in products]
        self.assertEqual(prices, sorted(prices))

        # 2. Add a product review and verify average rating & review count update
        target_id = products[0]["id"]
        initial_count = products[0]["review_count"]

        rev_res = self.client.post(
            f"/api/products/{target_id}/reviews",
            json={
                "author_name": "Guilherme Teste",
                "rating": 5,
                "comment": "Acabamento de primeira linha e latencia zero.",
            },
        )
        self.assertEqual(rev_res.status_code, 201)

        prod_res = self.client.get(f"/api/products/{target_id}")
        self.assertEqual(prod_res.status_code, 200)
        updated_prod = prod_res.json()
        self.assertEqual(updated_prod["review_count"], initial_count + 1)
        self.assertGreater(updated_prod["avg_rating"], 0.0)

        # Clean up test review
        from app.database import get_db_connection
        conn = get_db_connection()
        conn.execute("DELETE FROM reviews WHERE id = ?;", (rev_res.json()["id"],))
        conn.commit()
        conn.close()

    def test_02_coupons_shipping_and_checkout(self) -> None:
        # 1. Validate coupon DEV10
        cp_res = self.client.post(
            "/api/coupons/validate",
            json={"code": "DEV10", "subtotal": 200.0},
        )
        self.assertEqual(cp_res.status_code, 200)
        cp_data = cp_res.json()
        self.assertTrue(cp_data["valid"])
        self.assertEqual(cp_data["discount_amount"], 20.0)

        # 2. Quote shipping for PR (80010-000) under R$ 500
        sh_res = self.client.post(
            "/api/shipping/quote",
            json={"zip_code": "80010-000", "subtotal": 200.0},
        )
        self.assertEqual(sh_res.status_code, 200)
        sh_data = sh_res.json()
        self.assertEqual(sh_data["cost"], 18.90)
        self.assertFalse(sh_data["free_shipping_applied"])

        # 3. Quote shipping with SIDI20 (includes free shipping)
        sh_free = self.client.post(
            "/api/shipping/quote",
            json={"zip_code": "80010-000", "subtotal": 200.0, "coupon_code": "SIDI20"},
        )
        self.assertEqual(sh_free.status_code, 200)
        self.assertEqual(sh_free.json()["cost"], 0.0)
        self.assertTrue(sh_free.json()["free_shipping_applied"])

    def test_03_order_lifecycle_tracking_and_admin_restock(self) -> None:
        # Check initial stock of product 1
        p1_before = self.client.get("/api/products/1").json()
        initial_stock = p1_before["stock"]

        # Create order with coupon DEV10 and cartao
        checkout_res = self.client.post(
            "/api/checkout",
            json={
                "customer_name": "Guilherme Weber",
                "customer_email": "guilherme.weber@sidi.dev",
                "customer_address": "Av. Batel, 1500 - Curitiba/PR",
                "zip_code": "80420-090",
                "payment_method": "cartao",
                "coupon_code": "DEV10",
                "items": [{"product_id": 1, "quantity": 2}],
            },
        )
        self.assertEqual(checkout_res.status_code, 200)
        order = checkout_res.json()
        order_id = order["order_id"]

        # Verify stock decreased by 2
        p1_after_order = self.client.get("/api/products/1").json()
        self.assertEqual(p1_after_order["stock"], initial_stock - 2)

        # Search order by email and by order_id
        search_email = self.client.get("/api/orders/search?q=guilherme.weber@sidi.dev")
        self.assertEqual(search_email.status_code, 200)
        self.assertTrue(any(o["order_id"] == order_id for o in search_email.json()))

        # Render HTML views (/track and /order/{id})
        track_html = self.client.get(f"/track?q={order_id}")
        self.assertEqual(track_html.status_code, 200)
        self.assertIn(order_id, track_html.text)

        # Admin updates status to 'Em Separacao'
        st_res = self.client.patch(
            f"/api/admin/orders/{order_id}/status",
            json={"status": "Em Separacao"},
        )
        self.assertEqual(st_res.status_code, 200)
        self.assertEqual(st_res.json()["status"], "Em Separacao")

        # Admin cancels order -> stock must be automatically restocked!
        cancel_res = self.client.patch(
            f"/api/admin/orders/{order_id}/status",
            json={"status": "Cancelado"},
        )
        self.assertEqual(cancel_res.status_code, 200)
        self.assertEqual(cancel_res.json()["status"], "Cancelado")

        p1_after_cancel = self.client.get("/api/products/1").json()
        self.assertEqual(p1_after_cancel["stock"], initial_stock)

        # Clean up test orders by guilherme.weber@sidi.dev and test review
        from app.database import get_db_connection
        conn = get_db_connection()
        conn.execute("DELETE FROM reviews WHERE author_name = 'Guilherme Teste';")
        conn.execute("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE customer_email = 'guilherme.weber@sidi.dev');")
        conn.execute("DELETE FROM orders WHERE customer_email = 'guilherme.weber@sidi.dev';")
        conn.commit()
        conn.close()

    def test_04_admin_crud_products_and_metrics(self) -> None:
        # Admin page and metrics
        admin_html = self.client.get("/admin")
        self.assertEqual(admin_html.status_code, 200)

        metrics_res = self.client.get("/api/admin/metrics")
        self.assertEqual(metrics_res.status_code, 200)
        self.assertIn("total_revenue", metrics_res.json())

        # Create product via Admin API
        create_res = self.client.post(
            "/api/admin/products",
            json={
                "name": "Keycap Puller Titanio CNC",
                "category": "Perifericos",
                "price": 89.90,
                "description": "Extrator de switches e keycaps em titanio usinado.",
                "stock": 12,
                "badge": " CNC",
                "specs": "Material: Titanio Grau 5 | Peso: 32g",
            },
        )
        self.assertEqual(create_res.status_code, 201)
        new_prod = create_res.json()
        prod_id = new_prod["id"]

        # Update product stock and price
        upd_res = self.client.put(
            f"/api/admin/products/{prod_id}",
            json={"price": 79.90, "stock": 4},
        )
        self.assertEqual(upd_res.status_code, 200)
        self.assertEqual(upd_res.json()["price"], 79.90)
        self.assertEqual(upd_res.json()["stock"], 4)

        # Delete test product to keep catalog clean
        del_res = self.client.delete(f"/api/admin/products/{prod_id}")
        self.assertEqual(del_res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
