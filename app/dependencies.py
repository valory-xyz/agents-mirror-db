from fastapi import HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from .db import get_db
from .models.models import APIKey

API_KEY_NAME = "access-token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)):
    if api_key_header:
        db_api_key = db.query(APIKey).filter(APIKey.key == api_key_header).first()
        if db_api_key:
            return db_api_key.key
    raise HTTPException(
        status_code=403,
        detail="Could not validate credentials",
    )