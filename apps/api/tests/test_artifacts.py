import pytest
import uuid
from sqlalchemy import delete
from unittest.mock import patch
from tests.conftest import test_sessionmaker
from models.paper import Paper
from models.artifact import Artifact

@pytest.mark.asyncio
async def test_create_and_delete_artifact(client, auth_headers):
    
    paper_id = uuid.uuid4()
    paper = Paper(
        id=paper_id,
        title="Attention Is All You Need",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        authors=["Ashish Vaswani"],
        pdf_processed=True
    )
    
    async with test_sessionmaker() as session:
        session.add(paper)
        await session.commit()

    payload = {"paper_id": str(paper_id)}
    artifact_id = None
    try:
        with patch("routers.artifacts.generate_artifact.delay") as mock_delay, \
             patch("routers.artifacts.check_usage_limit", return_value=(True, None)):
            response = await client.post("/artifacts", json=payload, headers=auth_headers)
            assert response.status_code == 201
            data = response.json()
            assert data["paper_id"] == str(paper_id)
            assert data["status"] == "queued"
            mock_delay.assert_called_once()
            artifact_id = data["id"]

            status_resp = await client.get(f"/artifacts/{artifact_id}/status", headers=auth_headers)
            assert status_resp.status_code == 200
            assert status_resp.json()["status"] == "queued"

            del_resp = await client.delete(f"/artifacts/{artifact_id}", headers=auth_headers)
            assert del_resp.status_code == 204
    finally:
        async with test_sessionmaker() as session:
            if artifact_id:
                await session.execute(delete(Artifact).where(Artifact.id == uuid.UUID(artifact_id)))
            await session.execute(delete(Paper).where(Paper.id == paper_id))
            await session.commit()
