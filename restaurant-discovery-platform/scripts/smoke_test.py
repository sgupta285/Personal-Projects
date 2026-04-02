from datetime import datetime, timedelta, timezone

import httpx

BASE_URL = "http://localhost:8000"


def main() -> None:
    register = {"email": "smoke@example.com", "full_name": "Smoke Tester", "password": "password123"}
    httpx.post(f"{BASE_URL}/api/v1/auth/register", json=register)
    login = httpx.post(f"{BASE_URL}/api/v1/auth/login", json={"email": register["email"], "password": register["password"]})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    restaurants = httpx.get(f"{BASE_URL}/api/v1/restaurants", params={"city": "Chicago"}).json()
    assert restaurants["total"] > 0

    reservation_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    reservation = httpx.post(
        f"{BASE_URL}/api/v1/reservations/restaurants/1",
        json={"reservation_time": reservation_time, "party_size": 2},
        headers=headers,
    )
    reservation.raise_for_status()
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
