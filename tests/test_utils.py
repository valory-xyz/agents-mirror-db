import time

import pytest
from eth_account import Account as EthAccount
from eth_account.messages import encode_defunct
from fastapi import HTTPException

from app.utils import generate_api_key, is_timestamp_valid, verify_signature


class TestGenerateApiKey:
    def test_returns_string(self):
        key = generate_api_key()
        assert isinstance(key, str)
        assert len(key) > 20

    def test_unique_keys(self):
        keys = {generate_api_key() for _ in range(50)}
        assert len(keys) == 50


class TestVerifySignature:
    def test_valid_signature(self):
        account = EthAccount.create()
        message = "test message"
        signable = encode_defunct(text=message)
        signed = account.sign_message(signable)

        assert verify_signature(message, signed.signature.hex(), account.address)

    def test_wrong_address(self):
        account = EthAccount.create()
        other = EthAccount.create()
        message = "test message"
        signable = encode_defunct(text=message)
        signed = account.sign_message(signable)

        assert not verify_signature(message, signed.signature.hex(), other.address)

    def test_wrong_message(self):
        account = EthAccount.create()
        signable = encode_defunct(text="original")
        signed = account.sign_message(signable)

        # Signature was for "original", verifying against "tampered"
        assert not verify_signature("tampered", signed.signature.hex(), account.address)

    def test_malformed_signature_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_signature("msg", "not-a-signature", "0x0000")
        assert exc_info.value.status_code == 400


class TestIsTimestampValid:
    def test_recent_timestamp(self):
        assert is_timestamp_valid(int(time.time()))

    def test_expired_timestamp(self):
        old = int(time.time()) - 600
        assert not is_timestamp_valid(old)

    def test_custom_max_age(self):
        ts = int(time.time()) - 10
        assert is_timestamp_valid(ts, max_age_seconds=20)
        assert not is_timestamp_valid(ts, max_age_seconds=5)
