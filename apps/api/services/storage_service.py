import logging
import os
from core.config import settings

logger = logging.getLogger("services.storage_service")


class StorageService:
    """Local filesystem storage service. Replaces Supabase Storage."""

    def _get_local_path(self, key: str) -> str:
        scratch_dir = settings.STORAGE_DIR
        full_path = os.path.join(scratch_dir, key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path

    async def ensure_bucket(self) -> bool:
        return True

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        local_path = self._get_local_path(key)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)
        logger.info(f"[StorageService] Saved to local storage: {local_path}")
        return local_path

    async def download(self, key: str) -> bytes:
        local_path = self._get_local_path(key)
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"File not found in local storage: {local_path}")
        with open(local_path, "rb") as f:
            return f.read()

    async def delete(self, key: str) -> None:
        local_path = self._get_local_path(key)
        if os.path.exists(local_path):
            os.remove(local_path)

    async def signed_url(self, key: str, expires_in: int = 3600) -> str:
        local_path = self._get_local_path(key)
        if os.path.exists(local_path):
            return f"file://{local_path}"
        raise FileNotFoundError(f"File not found: {key}")

    async def exists(self, key: str) -> bool:
        return os.path.exists(self._get_local_path(key))


storage_service = StorageService()
