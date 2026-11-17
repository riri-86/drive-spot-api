import os
import secrets

from fastapi import Header, HTTPException


def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("ADMIN_API_KEY")
    if expected is None:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY が設定されていません")
    if x_api_key is None or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API key")
