"""
Smoke tests for E-Commerce Backend API.
Uses SQLite in-memory for fast isolated testing.
"""

import os
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport

# Force SQLite in-memory for tests
os.environ["ECOM_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ECOM_REDIS_ENABLED"] = "false"

from app.main import app
from app.models.database import init_db


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    await init_db()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ---- Health ----
@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "docs" in resp.json()


# ---- Categories ----
@pytest.mark.asyncio
async def test_create_and_list_categories(client):
    resp = await client.post("/api/v1/categories", json={"name": "TestCat", "description": "Test"})
    assert resp.status_code == 201
    cat = resp.json()
    assert cat["name"] == "TestCat"

    resp = await client.get("/api/v1/categories")
    assert resp.status_code == 200
    cats = resp.json()
    assert len(cats) >= 1


# ---- Customers ----
@pytest.mark.asyncio
async def test_create_customer(client):
    resp = await client.post("/api/v1/customers", json={"email": "test@test.com", "name": "Test User"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@test.com"


@pytest.mark.asyncio
async def test_duplicate_customer_email(client):
    await client.post("/api/v1/customers", json={"email": "dup@test.com", "name": "First"})
    resp = await client.post("/api/v1/customers", json={"email": "dup@test.com", "name": "Second"})
    assert resp.status_code == 409


# ---- Products ----
@pytest.mark.asyncio
async def test_create_and_list_products(client):
    # Create category first
    cat_resp = await client.post("/api/v1/categories", json={"name": "ProdCat"})
    cat_id = cat_resp.json()["id"]

    # Create product
    resp = await client.post("/api/v1/products", json={
        "name": "Test Widget",
        "price": 29.99,
        "stock": 100,
        "sku": "SKU-TEST-001",
        "category_id": cat_id,
    })
    assert resp.status_code == 201
    product = resp.json()
    assert product["name"] == "Test Widget"
    assert product["price"] == 29.99

    # List products
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_product_detail(client):
    cat_resp = await client.post("/api/v1/categories", json={"name": "DetailCat"})
    cat_id = cat_resp.json()["id"]

    create_resp = await client.post("/api/v1/products", json={
        "name": "Detail Widget",
        "price": 49.99,
        "stock": 50,
        "sku": "SKU-DETAIL-001",
        "category_id": cat_id,
    })
    product_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/products/{product_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == product_id


@pytest.mark.asyncio
async def test_product_not_found(client):
    resp = await client.get("/api/v1/products/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_product(client):
    create_resp = await client.post("/api/v1/products", json={
        "name": "Update Me",
        "price": 10.0,
        "stock": 20,
        "sku": "SKU-UPDATE-001",
    })
    pid = create_resp.json()["id"]

    resp = await client.put(f"/api/v1/products/{pid}", json={"price": 15.0, "stock": 30})
    assert resp.status_code == 200
    assert resp.json()["price"] == 15.0
    assert resp.json()["stock"] == 30


@pytest.mark.asyncio
async def test_filter_products_by_price(client):
    resp = await client.get("/api/v1/products?min_price=10&max_price=100")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_search_products(client):
    resp = await client.get("/api/v1/products?search=Widget")
    assert resp.status_code == 200


# ---- Orders ----
@pytest.mark.asyncio
async def test_create_order(client):
    # Create customer
    cust_resp = await client.post("/api/v1/customers", json={"email": "order@test.com", "name": "Order User"})
    cust_id = cust_resp.json()["id"]

    # Create product
    prod_resp = await client.post("/api/v1/products", json={
        "name": "Order Product",
        "price": 25.00,
        "stock": 50,
        "sku": "SKU-ORDER-001",
    })
    prod_id = prod_resp.json()["id"]

    # Create order
    resp = await client.post("/api/v1/orders", json={
        "customer_id": cust_id,
        "items": [{"product_id": prod_id, "quantity": 2}],
    })
    assert resp.status_code == 201
    order = resp.json()
    assert order["total"] == 50.00
    assert len(order["items"]) == 1

    # Verify stock decreased
    prod_resp = await client.get(f"/api/v1/products/{prod_id}")
    assert prod_resp.json()["stock"] == 48


@pytest.mark.asyncio
async def test_order_insufficient_stock(client):
    cust_resp = await client.post("/api/v1/customers", json={"email": "nostock@test.com", "name": "No Stock"})
    cust_id = cust_resp.json()["id"]

    prod_resp = await client.post("/api/v1/products", json={
        "name": "Low Stock Item",
        "price": 10.0,
        "stock": 1,
        "sku": "SKU-LOW-001",
    })
    prod_id = prod_resp.json()["id"]

    resp = await client.post("/api/v1/orders", json={
        "customer_id": cust_id,
        "items": [{"product_id": prod_id, "quantity": 5}],
    })
    assert resp.status_code == 400
    assert "Insufficient stock" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_cancel_order_restores_stock(client):
    cust_resp = await client.post("/api/v1/customers", json={"email": "cancel@test.com", "name": "Cancel User"})
    cust_id = cust_resp.json()["id"]

    prod_resp = await client.post("/api/v1/products", json={
        "name": "Cancel Product",
        "price": 20.0,
        "stock": 100,
        "sku": "SKU-CANCEL-001",
    })
    prod_id = prod_resp.json()["id"]

    order_resp = await client.post("/api/v1/orders", json={
        "customer_id": cust_id,
        "items": [{"product_id": prod_id, "quantity": 10}],
    })
    order_id = order_resp.json()["id"]

    # Stock should be 90
    prod_check = await client.get(f"/api/v1/products/{prod_id}")
    assert prod_check.json()["stock"] == 90

    # Cancel order
    resp = await client.patch(f"/api/v1/orders/{order_id}/status?status=cancelled")
    assert resp.status_code == 200

    # Stock restored to 100
    prod_check = await client.get(f"/api/v1/products/{prod_id}")
    assert prod_check.json()["stock"] == 100
