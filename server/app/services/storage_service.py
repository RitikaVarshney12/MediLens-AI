import httpx

from app.core.config import settings


class StorageError(Exception):
    pass


async def upload_file_to_storage(path: str, content: bytes, content_type: str) -> None:
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.STORAGE_BUCKET}/{path}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": content_type or "application/octet-stream",
        "x-upsert": "false",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, content=content, headers=headers)

    if response.status_code >= 400:
        raise StorageError(f"Supabase Storage upload failed ({response.status_code}): {response.text}")