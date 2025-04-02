import secrets
import time
from eth_account.messages import encode_defunct
from eth_account import Account
from fastapi import HTTPException

def generate_api_key():
    return secrets.token_urlsafe(32)

def verify_signature(message: str, signature: str, address: str) -> bool:
    """
    Verify an ECDSA signature.
    
    Args:
        message: The message that was signed
        signature: The signature to verify
        address: The Ethereum address (public key) of the signer
        
    Returns:
        bool: True if the signature is valid, False otherwise
    """
    try:
        # Create a signable message from the text
        signable_message = encode_defunct(text=message)
        
        # Recover the address from the signature
        # Account.recover_message is a static method, not an instance method
        recovered_address = Account.recover_message(signable_message, signature=signature)
        
        # Compare the recovered address with the provided address
        return recovered_address.lower() == address.lower()
    except Exception as e:
        # Print the exception for debugging
        print(f"Error verifying signature: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

def is_timestamp_valid(timestamp: int, max_age_seconds: int = 300) -> bool:
    """
    Check if a timestamp is within the allowed time window.
    
    Args:
        timestamp: The timestamp to check (in seconds)
        max_age_seconds: Maximum age of the timestamp in seconds (default: 5 minutes)
        
    Returns:
        bool: True if the timestamp is valid, False otherwise
    """
    current_time = int(time.time())
    return current_time - timestamp <= max_age_seconds

# Removed generate_auth_message function as it's no longer needed
