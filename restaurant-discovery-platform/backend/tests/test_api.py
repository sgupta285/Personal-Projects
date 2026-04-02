from datetime import datetime, timedelta, timezone


def register_and_login(client, email="sam@example.com", password="password123", register=True):
    if register:
        client.post(
            "/api/v1/auth/register",
            json={"email": email, "full_name": "Sam Tester", "password": password},
        )
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_search_and_filter(client):
    response = client.get("/api/v1/restaurants", params={"city": "Chicago", "vegetarian": True})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 2
    assert all(item["city"] == "Chicago" for item in payload["items"])


def test_review_moderation_flow(client):
    user_headers = register_and_login(client)
    create_response = client.post(
        "/api/v1/reviews/restaurants/1",
        json={"rating": 5, "title": "Great dinner", "body": "Service was fast and the food felt balanced and fresh."},
        headers=user_headers,
    )
    assert create_response.status_code == 201
    review_id = create_response.json()["id"]

    admin_headers = register_and_login(client, email="moderator.admin@example.com", register=False)
    pending_response = client.get("/api/v1/reviews/moderation/pending", headers=admin_headers)
    assert pending_response.status_code == 200
    assert any(item["id"] == review_id for item in pending_response.json())

    moderate_response = client.post(
        f"/api/v1/reviews/moderation/{review_id}",
        json={"action": "approve"},
        headers=admin_headers,
    )
    assert moderate_response.status_code == 200
    restaurant_response = client.get("/api/v1/restaurants/1")
    assert restaurant_response.json()["review_count"] == 1


def test_reservation_booking(client):
    headers = register_and_login(client)
    reservation_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    response = client.post(
        "/api/v1/reservations/restaurants/1",
        json={"reservation_time": reservation_time, "party_size": 4, "notes": "Window seat if possible"},
        headers=headers,
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["provider_name"] == "mock-opentable"
    assert payload["provider_confirmation_code"].startswith("RES-")


def test_distance_sorting(client):
    response = client.get(
        "/api/v1/restaurants",
        params={"sort_by": "distance", "user_lat": 41.89, "user_lon": -87.64},
    )
    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["distance_km"] <= items[-1]["distance_km"]
