import pytest
from models.user import User

@pytest.mark.asyncio
async def test_get_current_user_profile_authorized(client, auth_headers):
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["email"] == "test@shouko-ai.app"

@pytest.mark.asyncio
async def test_patch_user_profile(client, auth_headers):
    payload = {
        "name": "Dr. Shouko AI",
        "interest_profile": {
            "topics": ["Attention Mechanisms"],
            "keywords": ["Transformer"],
            "authors": ["Ashish Vaswani"],
            "categories": ["cs.CL"]
        }
    }
    response = await client.patch("/users/me", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dr. Shouko AI"
    assert "topics" in data["interest_profile"]
    assert "Attention Mechanisms" in data["interest_profile"]["topics"]
