import uuid
from pathlib import Path

import boto3
from fastapi import HTTPException, UploadFile

from app.core.config import get_settings


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


async def save_upload(file: UploadFile, user_id: str) -> tuple[str, str]:
    settings = get_settings()
    ext = ALLOWED_CONTENT_TYPES.get(file.content_type or "")
    if not ext:
        raise HTTPException(status_code=400, detail="仅支持 jpg / jpeg / png / webp 图片")

    content = await file.read()
    if len(content) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"单张图片不能超过 {settings.max_upload_mb}MB")

    key = f"users/{user_id}/mistakes/{uuid.uuid4()}.{ext}"
    if settings.storage_mode == "s3":
        return save_to_s3(key, content, file.content_type or "application/octet-stream")
    return save_to_local(key, content)


def save_to_local(key: str, content: bytes) -> tuple[str, str]:
    settings = get_settings()
    target = Path(settings.upload_dir) / key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    return f"/api/files/{key}", key


def save_to_s3(key: str, content: bytes, content_type: str) -> tuple[str, str]:
    settings = get_settings()
    if not settings.s3_bucket_name:
        raise HTTPException(status_code=500, detail="对象存储未配置 S3_BUCKET_NAME")
    client = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
    )
    client.put_object(Bucket=settings.s3_bucket_name, Key=key, Body=content, ContentType=content_type)
    if settings.s3_public_base_url:
        return f"{settings.s3_public_base_url.rstrip('/')}/{key}", key
    return client.generate_presigned_url("get_object", Params={"Bucket": settings.s3_bucket_name, "Key": key}, ExpiresIn=3600), key
