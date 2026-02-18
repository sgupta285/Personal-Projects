"""
Locust load test for E-Commerce Backend API.
Simulates realistic e-commerce traffic patterns:
  - 60% product browsing (GET /products)
  - 15% product detail (GET /products/:id)
  - 10% category browsing
  - 10% order creation
  - 5% customer operations

Run: locust -f scripts/locustfile.py --host=http://localhost:8000
"""

import random
import string
from locust import HttpUser, task, between, events


class ECommerceUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self):
        """Setup: fetch product/customer IDs for realistic flows."""
        self._product_ids = []
        self._customer_ids = []
        self._category_ids = []

        # Fetch products
        try:
            resp = self.client.get("/api/v1/products?page_size=50")
            if resp.status_code == 200:
                data = resp.json()
                self._product_ids = [p["id"] for p in data.get("items", [])]
        except Exception:
            pass

        # Fetch categories
        try:
            resp = self.client.get("/api/v1/categories")
            if resp.status_code == 200:
                self._category_ids = [c["id"] for c in resp.json()]
        except Exception:
            pass

        # Fetch customers
        try:
            resp = self.client.get("/api/v1/customers")
            if resp.status_code == 200:
                self._customer_ids = [c["id"] for c in resp.json()]
        except Exception:
            pass

    @task(30)
    def browse_products(self):
        """Browse product listings with pagination."""
        page = random.randint(1, 3)
        page_size = random.choice([10, 20, 50])
        self.client.get(
            f"/api/v1/products?page={page}&page_size={page_size}",
            name="/api/v1/products"
        )

    @task(15)
    def browse_products_filtered(self):
        """Browse products with category/price filters."""
        params = {"page_size": 20}
        if self._category_ids:
            params["category_id"] = random.choice(self._category_ids)
        params["min_price"] = random.choice([0, 10, 25, 50])
        params["max_price"] = random.choice([100, 200, 300])
        self.client.get(
            "/api/v1/products",
            params=params,
            name="/api/v1/products?filtered"
        )

    @task(15)
    def view_product_detail(self):
        """View a single product."""
        if not self._product_ids:
            return
        pid = random.choice(self._product_ids)
        self.client.get(f"/api/v1/products/{pid}", name="/api/v1/products/:id")

    @task(10)
    def browse_categories(self):
        """Browse category list."""
        self.client.get("/api/v1/categories", name="/api/v1/categories")

    @task(10)
    def create_order(self):
        """Place an order with 1-3 random items."""
        if not self._product_ids or not self._customer_ids:
            return

        items = []
        for _ in range(random.randint(1, 3)):
            items.append({
                "product_id": random.choice(self._product_ids),
                "quantity": random.randint(1, 3),
            })

        self.client.post(
            "/api/v1/orders",
            json={
                "customer_id": random.choice(self._customer_ids),
                "items": items,
            },
            name="/api/v1/orders [POST]"
        )

    @task(5)
    def list_orders(self):
        """List recent orders."""
        self.client.get("/api/v1/orders?page_size=10", name="/api/v1/orders")

    @task(5)
    def search_products(self):
        """Search products by name."""
        terms = ["pro", "premium", "ultra", "wireless", "classic", "smart"]
        self.client.get(
            f"/api/v1/products?search={random.choice(terms)}",
            name="/api/v1/products?search"
        )

    @task(3)
    def health_check(self):
        """Health check."""
        self.client.get("/health", name="/health")

    @task(2)
    def view_customer(self):
        """View customer profile."""
        if not self._customer_ids:
            return
        cid = random.choice(self._customer_ids)
        self.client.get(f"/api/v1/customers/{cid}", name="/api/v1/customers/:id")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("\n" + "=" * 60)
    print("E-COMMERCE BACKEND LOAD TEST")
    print("=" * 60)
    print("Traffic mix: 60% browse, 15% detail, 10% orders, 10% categories, 5% other")
    print("=" * 60 + "\n")
