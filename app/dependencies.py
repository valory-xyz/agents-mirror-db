from fastapi import HTTPException, Security, Depends, Header, Request
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from typing import Optional
from .db import get_db
from .models import models
from .utils import verify_signature, is_timestamp_valid
from .schemas.schemas import SignatureAuth

API_KEY_NAME = "access-token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header), db: Session = Depends(get_db)):
    if api_key_header:
        db_api_key = db.query(models.APIKey).filter(models.APIKey.key == api_key_header).first()
        if db_api_key:
            return db_api_key.key
    raise HTTPException(
        status_code=403,
        detail="Could not validate credentials",
    )

async def verify_agent_signature(
    auth: SignatureAuth,
    db: Session = Depends(get_db)
):
    """
    Verify the ECDSA signature provided in the request body.
    
    Args:
        auth: The SignatureAuth object containing agent_id, signature, and message
    """
    # Check if the address is registered
    db_agent = db.query(models.AgentRegistry).filter(
        models.AgentRegistry.agent_id == auth.agent_id
    ).first()
    
    if not db_agent:
        raise HTTPException(
            status_code=401,
            detail="Invalid agent or address"
        )
    
    # Verify the signature
    if not verify_signature(auth.message, auth.signature, db_agent.eth_address):
        raise HTTPException(
            status_code=401,
            detail="Invalid signature"
        )
    
    # Return the agent ID for use in the endpoint
    return auth.agent_id
