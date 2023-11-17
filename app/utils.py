import base64, hashlib, re, json
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone

from . import crud
from core.redis import redis_pool


def not_authenticated() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Not authenticated'
    )


def is_valid_password(password):
    regex = re.compile(r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[\.\#\?\!\@\$\%\^\&\*\-\_]).{8,30}$', re.MULTILINE)
    if not regex.fullmatch(password):
        raise ValueError('Password must be 8-30 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.')
    return password


def create_short_id(original_url: str, length=7):
    timestamp = datetime.now().replace(tzinfo=timezone.utc).timestamp()
    to_encode = f"{original_url}{timestamp}"

    hashed_data = hashlib.sha256(to_encode.encode()).digest()
    b64_encoded_str = base64.urlsafe_b64encode(hashed_data).decode().rstrip('=')

    short_id = ''.join(char for char in b64_encoded_str if char.isalnum())
    return short_id[:length]


async def check_redis_cache(session: Session, short_id: str) -> str:
    cached_data = await redis_pool.get(short_id)
    if cached_data:
        return json.loads(cached_data)

    db_link = crud.get_link_by_short_id(session, short_id)
    if db_link:
        data_to_cache = {"url": db_link.original_url, "link_id": db_link.id}
        await redis_pool.set(short_id, json.dumps(data_to_cache))
        return data_to_cache
    
    return {}