import pytest
import uuid
from sqlalchemy import delete
from tests.conftest import test_sessionmaker
from models.collection import Collection

@pytest.mark.asyncio
async def test_collections_crud(client, auth_headers):
    
    payload = {
        "name": "Transformer Papers",
        "description": "Important publications in attention networks",
        "color": "#10B981"
    }
    
    collection_id = None
    try:
        response = await client.post("/collections", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Transformer Papers"
        assert data["description"] == "Important publications in attention networks"
        assert data["color"] == "#10B981"
        collection_id = data["id"]
        
        list_resp = await client.get("/collections", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) > 0
        assert any(c["id"] == collection_id for c in list_resp.json())

        update_payload = {
            "name": "Self-Attention Papers",
            "color": "#3B82F6"
        }
        up_resp = await client.put(f"/collections/{collection_id}", json=update_payload, headers=auth_headers)
        assert up_resp.status_code == 200
        assert up_resp.json()["name"] == "Self-Attention Papers"
        assert up_resp.json()["color"] == "#3B82F6"

        del_resp = await client.delete(f"/collections/{collection_id}", headers=auth_headers)
        assert del_resp.status_code == 204
        collection_id = None
    finally:
        if collection_id:
            async with test_sessionmaker() as session:
                await session.execute(delete(Collection).where(Collection.id == uuid.UUID(collection_id)))
                await session.commit()
