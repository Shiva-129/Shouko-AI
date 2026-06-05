from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
import uuid


class MockUser:
    def __init__(
        self,
        id: str = "00000000-0000-0000-0000-000000000000",
        email: str = "mock@shouko-ai.app",
        name: str | None = "Mock User",
        plan: str = "free",
    ):
        self.id = id
        self.email = email
        self.name = name
        self.plan = plan
        self.avatar_url = None
        self.onboarded_at = None
        self.created_at = "2026-01-01T00:00:00+00:00"
        self.interest_profile = {
            "topics": ["Transformers", "Neural Networks"],
            "keywords": ["Attention", "Transformer"],
            "authors": [],
            "categories": ["cs.CL", "cs.LG"],
        }
