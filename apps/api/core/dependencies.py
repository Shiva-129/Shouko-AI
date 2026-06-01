from fastapi import Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.exceptions import UnauthorizedException

class MockUser:
    def __init__(self, id: str = "00000000-0000-0000-0000-000000000000", email: str = "mock@paperbrain.app"):
        self.id = id
        self.email = email

async def get_current_user(authorization: str = Header(default="Bearer mock-token")) -> MockUser:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(message="Invalid authorization token format")
    # For scaffolding, return a mock user. Later this verifies the Supabase JWT.
    return MockUser()
