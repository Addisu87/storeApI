from app.tests.helpers import random_email, random_lower_string
from fastapi import status


def test_complete_user_workflow(client):
    # 1. Register new user
    email = random_email()
    password = random_lower_string()
    register_data = {"email": email, "password": password}

    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == status.HTTP_201_CREATED
    user_id = response.json()["id"]

    # 2. Login
    login_data = {"username": email, "password": password}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Create an item
    item_data = {
        "title": random_lower_string(),
        "description": random_lower_string(),
    }
    response = client.post(
        "/api/v1/items/",
        headers=headers,
        json=item_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    item_id = response.json()["id"]

    # 4. Read item
    response = client.get(
        f"/api/v1/items/{item_id}",
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == item_data["title"]

    # 5. Update user profile
    new_name = random_lower_string()
    response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"full_name": new_name},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == new_name

    # 6. Request password reset
    response = client.post(f"/api/v1/auth/password-recovery/{email}")
    assert response.status_code == status.HTTP_200_OK
