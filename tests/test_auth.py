import pytest
from eth_account import Account as EthAccount
from fastapi import HTTPException

from app.dependencies import get_api_key, verify_agent_signature
from app.models.models import AgentRegistry, AgentType
from app.schemas.schemas import SignatureAuth
from tests.conftest import make_raw_client, sign_message


class TestApiKeyAuth:
    @pytest.mark.anyio
    async def test_valid_key(self, db, agent):
        result = await get_api_key("seed-api-key", db)
        assert result == "seed-api-key"

    @pytest.mark.anyio
    async def test_invalid_key(self, db):
        with pytest.raises(HTTPException) as exc_info:
            await get_api_key("bad-key", db)
        assert exc_info.value.status_code == 403

    @pytest.mark.anyio
    async def test_missing_key(self, db):
        with pytest.raises(HTTPException) as exc_info:
            await get_api_key(None, db)
        assert exc_info.value.status_code == 403

    def test_protected_endpoint_without_key(self, db, agent):
        """HTTP-level test: accessing a protected endpoint with no API key."""
        c = make_raw_client(db)
        resp = c.get(f"/api/agents/{agent.agent_id}")
        assert resp.status_code == 403


class TestSignatureAuth:
    @pytest.mark.anyio
    async def test_valid_signature(self, db, eth_account):
        # Create agent type + registry with the test account's address
        at = AgentType(type_name="AuthTest", description="test")
        db.add(at)
        db.commit()
        db.refresh(at)

        reg = AgentRegistry(
            agent_name="auth-agent",
            type_id=at.type_id,
            eth_address=eth_account.address,
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        message = "auth test message"
        signature = sign_message(eth_account, message)

        auth = SignatureAuth(
            agent_id=reg.agent_id, signature=signature, message=message
        )
        result = await verify_agent_signature(auth, db)
        assert result == reg.agent_id

    @pytest.mark.anyio
    async def test_agent_not_in_registry(self, db, eth_account):
        message = "msg"
        signature = sign_message(eth_account, message)

        auth = SignatureAuth(agent_id=9999, signature=signature, message=message)
        with pytest.raises(HTTPException) as exc_info:
            await verify_agent_signature(auth, db)
        assert exc_info.value.status_code == 401

    @pytest.mark.anyio
    async def test_wrong_signature(self, db, eth_account):
        at = AgentType(type_name="AuthTest2", description="test")
        db.add(at)
        db.commit()
        db.refresh(at)

        reg = AgentRegistry(
            agent_name="auth-agent-2",
            type_id=at.type_id,
            eth_address=eth_account.address,
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        # Sign with a DIFFERENT account
        wrong_account = EthAccount.create()
        message = "msg"
        signature = sign_message(wrong_account, message)

        auth = SignatureAuth(
            agent_id=reg.agent_id, signature=signature, message=message
        )
        with pytest.raises(HTTPException) as exc_info:
            await verify_agent_signature(auth, db)
        assert exc_info.value.status_code == 401

    def test_sig_protected_endpoint_via_http(self, db, eth_account):
        """HTTP-level test: DELETE agent-type requires valid signature."""
        at = AgentType(type_name="ToDelete", description="bye")
        db.add(at)
        db.commit()
        db.refresh(at)

        reg = AgentRegistry(
            agent_name="deleter",
            type_id=at.type_id,
            eth_address=eth_account.address,
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)

        c = make_raw_client(db)
        message = "delete type"
        signature = sign_message(eth_account, message)

        # DELETE /api/agent-types/{type_id} — body is just the SignatureAuth
        resp = c.request(
            "DELETE",
            f"/api/agent-types/{at.type_id}",
            json={
                "agent_id": reg.agent_id,
                "signature": signature,
                "message": message,
            },
        )
        assert resp.status_code == 200
        assert resp.json()["type_id"] == at.type_id
