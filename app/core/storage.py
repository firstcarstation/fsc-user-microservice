from __future__ import annotations

import os
import uuid

from app.core.config import settings
from app.core.exceptions import AppException


def save_profile_image(user_id: str, file_bytes: bytes, filename: str) -> str:
    max_b = settings.UPLOAD_MAX_MB * 1024 * 1024
    if len(file_bytes) > max_b:
        raise AppException("File too large", status_code=400)

    bucket = settings.S3_BUCKET_NAME.strip()
    if bucket:
        return _upload_s3(user_id, file_bytes, filename, bucket)

    root = os.path.abspath(settings.LOCAL_UPLOAD_DIR)
    sub = f"profiles/{user_id}"
    safe = f"{uuid.uuid4().hex}_{os.path.basename(filename) or 'photo'}"
    dest_dir = os.path.join(root, sub)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, safe)
    with open(dest_path, "wb") as f:
        f.write(file_bytes)
    rel = f"/uploads/{sub}/{safe}".replace("\\", "/")
    return f"{settings.PUBLIC_APP_URL.rstrip('/')}{rel}"


def _upload_s3(user_id: str, file_bytes: bytes, filename: str, bucket: str) -> str:
    try:
        import boto3
    except ImportError as e:
        raise AppException("S3 not configured (boto3 missing)", status_code=500) from e

    key = f"profiles/{user_id}/{uuid.uuid4().hex}_{os.path.basename(filename) or 'photo'}"
    session = boto3.session.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        region_name=settings.AWS_REGION,
    )
    client = session.client("s3")
    client.put_object(Bucket=bucket, Key=key, Body=file_bytes)
    base = settings.S3_PUBLIC_BASE_URL.strip()
    if base:
        return f"{base.rstrip('/')}/{key}"
    return f"https://{bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"
