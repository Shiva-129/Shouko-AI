import asyncio
import time
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.config import settings
from models.user import User
from core.rate_limit import RateLimiter
from routers.billing import billing_service
import stripe

# Database connection Setup
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class MockPipeline:
    def __init__(self, db_dict):
        self.db = db_dict
        self.commands = []

    def zremrangebyscore(self, key, min_val, max_val):
        self.commands.append(("zrem", key, min_val, max_val))
        return self

    def zadd(self, key, mapping):
        self.commands.append(("zadd", key, mapping))
        return self

    def zcard(self, key):
        self.commands.append(("zcard", key))
        return self

    def expire(self, key, time_val):
        self.commands.append(("expire", key, time_val))
        return self

    async def execute(self):
        results = []
        for cmd in self.commands:
            if cmd[0] == "zrem":
                key, _, max_val = cmd[1], cmd[2], cmd[3]
                if key not in self.db:
                    self.db[key] = {}
                to_remove = [m for m, s in self.db[key].items() if s <= max_val]
                for m in to_remove:
                    del self.db[key][m]
                results.append(len(to_remove))
            elif cmd[0] == "zadd":
                key, mapping = cmd[1], cmd[2]
                if key not in self.db:
                    self.db[key] = {}
                for m, s in mapping.items():
                    self.db[key][m] = s
                results.append(len(mapping))
            elif cmd[0] == "zcard":
                key = cmd[1]
                results.append(len(self.db.get(key, {})))
            elif cmd[0] == "expire":
                results.append(True)
        return results

class MockRedis:
    def __init__(self):
        self.db = {}

    def pipeline(self):
        return MockPipeline(self.db)

async def test_rate_limiting():
    print("\n--- Testing Redis-backed Rate Limiter ---")
    import core.rate_limit
    mock_redis = MockRedis()
    core.rate_limit.redis_client = mock_redis
    
    limiter = RateLimiter(limit=3, window=5, name="test_limit")
    identifier = f"user_{uuid.uuid4()}"
    
    # First 3 hits should pass
    for i in range(3):
        limited = await limiter.is_rate_limited(identifier)
        print(f"Hit {i+1}: Rate limited? {limited}")
        assert not limited, "Hit should be allowed under limit=3"
        
    # 4th hit should be limited
    limited = await limiter.is_rate_limited(identifier)
    print(f"Hit 4: Rate limited? {limited}")
    assert limited, "Hit 4 should be rate limited"
    
    # Wait for window to expire
    print("Waiting 6 seconds for window to clear...")
    await asyncio.sleep(6)
    
    # Should clear and allow again
    limited = await limiter.is_rate_limited(identifier)
    print(f"Hit after delay: Rate limited? {limited}")
    assert not limited, "Hit after delay should be allowed"
    print("✅ Rate limiter tests PASSED!")


async def test_billing_upgrades_downgrades():
    print("\n--- Testing Billing Webhook upgrades/downgrades ---")
    async with AsyncSessionLocal() as db:
        # Create a unique test user
        test_email = f"billing_tester_{uuid.uuid4()}@paperbrain.app"
        user = User(
            id=uuid.uuid4(),
            email=test_email,
            plan="free",
            stripe_customer_id=f"cus_{uuid.uuid4().hex[:10]}",
            interest_profile={"topics": []}
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        print(f"Seeded test user {user.email} with plan: {user.plan}")
        
        # 1. Simulate checkout/subscription success event
        # Mock Stripe event content
        mock_event = {
            "type": "customer.subscription.created",
            "data": {
                "object": {
                    "customer": user.stripe_customer_id,
                    "id": f"sub_{uuid.uuid4().hex[:10]}",
                    "metadata": {
                        "user_id": str(user.id)
                    }
                }
            }
        }
        
        # Override billing_service.construct_event to return our mock event
        original_construct = billing_service.construct_event
        billing_service.construct_event = lambda payload, sig: mock_event
        
        # Call the router webhook logic directly
        from fastapi import Request
        # Dummy request class
        class DummyRequest:
            async def body(self):
                return b"dummy_payload"
            headers = {"stripe-signature": "dummy_sig"}
            
        from routers.billing import stripe_webhook
        
        print("Invoking webhook customer.subscription.created...")
        await stripe_webhook(DummyRequest(), db)
        
        # Verify user is upgraded
        await db.refresh(user)
        print(f"User plan after upgrade webhook: {user.plan}")
        assert user.plan == "pro", "User should be upgraded to pro"
        assert user.stripe_subscription_id == mock_event["data"]["object"]["id"], "Subscription ID should be stored"
        
        # 2. Simulate subscription deletion event
        mock_delete_event = {
            "type": "customer.subscription.deleted",
            "data": {
                "object": {
                    "customer": user.stripe_customer_id,
                    "id": user.stripe_subscription_id
                }
            }
        }
        billing_service.construct_event = lambda payload, sig: mock_delete_event
        
        print("Invoking webhook customer.subscription.deleted...")
        await stripe_webhook(DummyRequest(), db)
        
        # Verify user is downgraded
        await db.refresh(user)
        print(f"User plan after downgrade webhook: {user.plan}")
        assert user.plan == "free", "User should be downgraded to free"
        assert user.stripe_subscription_id is None, "Subscription ID should be cleared"
        
        # Clean up
        await db.delete(user)
        await db.commit()
        print("✅ Webhook upgrade/downgrade logic tests PASSED!")
        
        # Restore billing service function
        billing_service.construct_event = original_construct


async def test_collections_crud():
    print("\n--- Testing Collections CRUD and Membership Operations ---")
    from routers.collections import (
        create_collection, 
        list_collections, 
        get_collection, 
        update_collection, 
        add_artifact_to_collection, 
        remove_artifact_from_collection, 
        delete_collection,
        CollectionCreate,
        CollectionUpdate,
        AddArtifactRequest
    )
    from models.paper import Paper
    from models.artifact import Artifact
    
    async with AsyncSessionLocal() as db:
        # 1. Setup mock User, Paper, and Artifact
        test_user = User(
            id=uuid.uuid4(),
            email=f"coll_tester_{uuid.uuid4()}@paperbrain.app",
            plan="free",
            interest_profile={"topics": []}
        )
        db.add(test_user)
        
        test_paper = Paper(
            id=uuid.uuid4(),
            title="Test Collections Paper",
            pdf_url="http://example.com/test_coll.pdf",
            source="manual"
        )
        db.add(test_paper)
        await db.flush()
        
        test_artifact = Artifact(
            id=uuid.uuid4(),
            user_id=test_user.id,
            paper_id=test_paper.id,
            status="ready"
        )
        db.add(test_artifact)
        await db.commit()
        
        print(f"Seeded User: {test_user.id}, Paper: {test_paper.id}, Artifact: {test_artifact.id}")
        
        # 2. Test create collection
        payload = CollectionCreate(name="My Research Folder", description="A test collection", color="#10B981")
        col_res = await create_collection(payload, db, test_user)
        col_id = uuid.UUID(col_res.id)
        print(f"Collection created: {col_res.name} (ID: {col_id})")
        assert col_res.name == "My Research Folder"
        assert col_res.color == "#10B981"
        
        # 3. Test list collections
        col_list = await list_collections(db, test_user)
        print(f"User collection count: {len(col_list)}")
        assert len(col_list) == 1
        assert col_list[0].id == str(col_id)
        
        # 4. Test update collection
        update_payload = CollectionUpdate(name="Renamed Research Folder", color="#F59E0B")
        updated_res = await update_collection(col_id, update_payload, db, test_user)
        print(f"Collection renamed: {updated_res.name}, color: {updated_res.color}")
        assert updated_res.name == "Renamed Research Folder"
        assert updated_res.color == "#F59E0B"
        
        # 5. Test add artifact to collection
        add_payload = AddArtifactRequest(artifact_id=str(test_artifact.id))
        membership_res = await add_artifact_to_collection(col_id, add_payload, db, test_user)
        print(f"Artifact added. Collection size: {len(membership_res.artifact_ids)}")
        assert str(test_artifact.id) in membership_res.artifact_ids
        
        # 6. Test get collection detail (with loaded artifacts)
        detail_res = await get_collection(col_id, db, test_user)
        print(f"Collection details loaded. Nested artifacts count: {len(detail_res.artifacts)}")
        assert len(detail_res.artifacts) == 1
        assert detail_res.artifacts[0]["id"] == str(test_artifact.id)
        assert detail_res.artifacts[0]["paper_title"] == "Test Collections Paper"
        
        # 7. Test remove artifact from collection
        removed_res = await remove_artifact_from_collection(col_id, test_artifact.id, db, test_user)
        print(f"Artifact removed. Collection size: {len(removed_res.artifact_ids)}")
        assert str(test_artifact.id) not in removed_res.artifact_ids
        
        # 8. Test delete collection
        await delete_collection(col_id, db, test_user)
        print("Collection deleted.")
        
        # Verify collection is gone
        final_list = await list_collections(db, test_user)
        assert len(final_list) == 0, "Collection should be deleted"
        
        # Cleanup seeded entities
        await db.delete(test_artifact)
        await db.delete(test_paper)
        await db.delete(test_user)
        await db.commit()
        print("✅ Collections CRUD and Membership operations tests PASSED!")


async def main():
    try:
        await test_rate_limiting()
        await test_billing_upgrades_downgrades()
        await test_collections_crud()
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
