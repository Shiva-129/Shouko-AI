import logging

logger = logging.getLogger("services.storage_service")

import os

from core.config import settings
from core.supabase_utils import normalize_supabase_url


class StorageService:
    """
    Abstract storage service that supports Supabase Storage in production and
    local filesystem storage in development mode.
    Methods use async HTTP calls (httpx) for Supabase Storage REST API.
    """

    def __init__(self):
        self._bucket_name = settings.SUPABASE_STORAGE_BUCKET or "papers"

        self._use_supabase = bool(
            settings.SUPABASE_URL
            and settings.SUPABASE_SERVICE_ROLE_KEY
            and settings.ENVIRONMENT not in ("development", "test")
        )

        if self._use_supabase:
            base_url = normalize_supabase_url(settings.SUPABASE_URL)
            self._storage_url = f"{base_url}/storage/v1"
            self._headers = {
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
            }

    def _get_local_path(self, key: str) -> str:
        scratch_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "scratch",
            "storage",
        )
        full_path = os.path.join(scratch_dir, key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path

    # ── Bucket management ──────────────────────────────────────────────

    async def ensure_bucket(self) -> bool:
        """
        Create the storage bucket if it does not exist.
        Called once at startup.
        Returns True if the bucket is ready.
        """
        if not self._use_supabase:
            return True  # local fallback — no bucket to create

        import httpx

        list_url = f"{self._storage_url}/bucket"
        async with httpx.AsyncClient(timeout=15.0) as client:
            # 1. Check if bucket already exists
            resp = await client.get(list_url, headers=self._headers)
            if resp.status_code == 200:
                buckets = resp.json()
                if any(b.get("name") == self._bucket_name for b in buckets):
                    logger.info(
                        f"[StorageService] Supabase bucket '{self._bucket_name}' already exists."
                    )
                    return True

            # 2. Create the bucket
            create_url = f"{self._storage_url}/bucket"
            resp = await client.post(
                create_url,
                json={
                    "name": self._bucket_name,
                    "public": True,
                    "file_size_limit": 52428800,
                    "allowed_mime_types": ["application/pdf"],
                },
                headers=self._headers,
            )
            if resp.status_code in (200, 201):
                logger.info(
                    f"[StorageService] Created Supabase bucket '{self._bucket_name}'."
                )
                return True
            else:
                logger.info(
                    f"[StorageService] Failed to create bucket: {resp.status_code} {resp.text}"
                )
                return False

    # ── Core operations ────────────────────────────────────────────────

    async def upload(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """
        Upload data to storage. In production, uploads to Supabase Storage.
        In development, stores on local filesystem.
        Returns the public URL or local path.
        """
        if self._use_supabase:
            import httpx

            url = f"{self._storage_url}/object/{self._bucket_name}/{key}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    url,
                    content=data,
                    headers={
                        **self._headers,
                        "Content-Type": content_type,
                    },
                )
                if resp.status_code not in (200, 201):
                    raise RuntimeError(
                        f"Supabase Storage upload failed: {resp.status_code} {resp.text}"
                    )
            logger.info(f"[StorageService] Uploaded to Supabase Storage: {key}")
            # Return a publicly accessible URL via the storage API
            return f"{self._storage_url}/object/public/{self._bucket_name}/{key}"
        else:
            local_path = self._get_local_path(key)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(data)
            logger.info(f"[StorageService] Saved to local storage: {local_path}")
            return local_path

    async def download(self, key: str) -> bytes:
        """Download data from storage."""
        if self._use_supabase:
            import httpx

            url = f"{self._storage_url}/object/{self._bucket_name}/{key}"
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.get(url, headers=self._headers)
                if resp.status_code != 200:
                    raise FileNotFoundError(
                        f"Object not found in Supabase Storage: {key} ({resp.status_code})"
                    )
                return resp.content
        else:
            local_path = self._get_local_path(key)
            if not os.path.exists(local_path):
                raise FileNotFoundError(
                    f"File not found in local storage: {local_path}"
                )
            with open(local_path, "rb") as f:
                return f.read()

    async def delete(self, key: str) -> None:
        """Delete data from storage."""
        if self._use_supabase:
            import httpx

            url = f"{self._storage_url}/object/{self._bucket_name}/{key}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.delete(url, headers=self._headers)
                if resp.status_code not in (200, 204):
                    logger.info(
                        f"[StorageService] Delete warning: {resp.status_code} {resp.text}"
                    )
        else:
            local_path = self._get_local_path(key)
            if os.path.exists(local_path):
                os.remove(local_path)

    async def signed_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a signed URL for temporary access to a private object."""
        if self._use_supabase:
            import httpx

            url = f"{self._storage_url}/object/sign/{self._bucket_name}/{key}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    url,
                    json={"expiresIn": expires_in},
                    headers=self._headers,
                )
                if resp.status_code != 200:
                    raise FileNotFoundError(
                        f"Failed to generate signed URL for '{key}': {resp.status_code} {resp.text}"
                    )
                data = resp.json()
                # Supabase returns {"signedURL": "/storage/v1/object/sign/..."}
                signed_path = data.get("signedURL") or data.get("url", "")
                if signed_path.startswith("/"):
                    base = normalize_supabase_url(settings.SUPABASE_URL)
                    return f"{base}{signed_path}"
                return signed_path
        else:
            local_path = self._get_local_path(key)
            if os.path.exists(local_path):
                return f"file://{local_path}"
            raise FileNotFoundError(f"File not found: {key}")

    async def exists(self, key: str) -> bool:
        """Check if a key exists in storage."""
        if self._use_supabase:
            import httpx

            url = f"{self._storage_url}/object/{self._bucket_name}/{key}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.head(url, headers=self._headers)
                return resp.status_code == 200
        else:
            return os.path.exists(self._get_local_path(key))


storage_service = StorageService()
