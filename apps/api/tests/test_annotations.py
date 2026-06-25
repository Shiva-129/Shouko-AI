import pytest
import uuid
from sqlalchemy import delete
from tests.conftest import test_sessionmaker
from models.paper import Paper
from models.artifact import Artifact
from models.annotation import Annotation

@pytest.mark.asyncio
async def test_annotations_crud(client, auth_headers):
    
    paper_id = uuid.uuid4()
    artifact_id = uuid.uuid4()
    
    paper = Paper(
        id=paper_id,
        title="Attention Is All You Need",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        authors=["Ashish Vaswani"]
    )
    
    artifact = Artifact(
        id=artifact_id,
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        paper_id=paper_id,
        status="ready"
    )

    # Seed data
    async with test_sessionmaker() as session:
        session.add(paper)
        await session.commit()

    async with test_sessionmaker() as session:
        session.add(artifact)
        await session.commit()

    annotation_id = None
    try:
        # 1. Create Annotation
        payload = {
            "artifact_id": str(artifact_id),
            "type": "note",
            "content": "This self-attention mechanism is highly parallelizable.",
            "meta_data": {"page": 2, "section": "Introduction"}
        }
        
        response = await client.post("/annotations", json=payload, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == payload["content"]
        assert data["type"] == "note"
        assert data["meta_data"]["section"] == "Introduction"
        annotation_id = data["id"]

        # 2. Get Single Annotation
        get_resp = await client.get(f"/annotations/{annotation_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["content"] == payload["content"]

        # 3. List Annotations
        list_resp = await client.get(f"/annotations?artifact_id={artifact_id}", headers=auth_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.json()) == 1
        assert list_resp.json()[0]["id"] == annotation_id

        # 4. Update Annotation
        update_payload = {
            "content": "Updated content: self-attention scales quadratically.",
            "meta_data": {"page": 3}
        }
        up_resp = await client.put(f"/annotations/{annotation_id}", json=update_payload, headers=auth_headers)
        assert up_resp.status_code == 200
        assert up_resp.json()["content"] == update_payload["content"]
        assert up_resp.json()["meta_data"]["page"] == 3
        # Ensure it merged with old metadata
        assert up_resp.json()["meta_data"]["section"] == "Introduction"

        # 5. Delete Annotation
        del_resp = await client.delete(f"/annotations/{annotation_id}", headers=auth_headers)
        assert del_resp.status_code == 204
        annotation_id = None
    finally:
        async with test_sessionmaker() as session:
            if annotation_id:
                await session.execute(delete(Annotation).where(Annotation.id == uuid.UUID(annotation_id)))
            await session.execute(delete(Artifact).where(Artifact.id == artifact_id))
            await session.execute(delete(Paper).where(Paper.id == paper_id))
            await session.commit()
