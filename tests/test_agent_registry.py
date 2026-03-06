from tests.conftest import make_client


class TestCreateAgentRegistry:
    def test_success(self, client, agent_type):
        resp = client.post(
            "/api/agent-registry/",
            json={
                "agent_name": "new-bot",
                "type_id": agent_type.type_id,
                "eth_address": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["agent_name"] == "new-bot"
        assert data["eth_address"] == "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        assert "agent_id" in data
        assert "created_at" in data

    def test_duplicate_address(self, client, registry, agent_type):
        resp = client.post(
            "/api/agent-registry/",
            json={
                "agent_name": "dup",
                "type_id": agent_type.type_id,
                "eth_address": registry.eth_address,
            },
        )
        assert resp.status_code == 409

    def test_type_not_found(self, client):
        resp = client.post(
            "/api/agent-registry/",
            json={
                "agent_name": "x",
                "type_id": 9999,
                "eth_address": "0x1111111111111111111111111111111111111111",
            },
        )
        assert resp.status_code == 404


class TestReadAgentRegistry:
    def test_list(self, client, registry):
        resp = client.get("/api/agent-registry/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_by_id(self, client, registry):
        resp = client.get(f"/api/agent-registry/{registry.agent_id}")
        assert resp.status_code == 200
        assert resp.json()["agent_name"] == "reg-agent"

    def test_by_id_not_found(self, client):
        resp = client.get("/api/agent-registry/9999")
        assert resp.status_code == 404

    def test_by_address(self, client, registry):
        resp = client.get(f"/api/agent-registry/address/{registry.eth_address}")
        assert resp.status_code == 200
        assert resp.json()["agent_id"] == registry.agent_id

    def test_by_address_not_found(self, client):
        resp = client.get(
            "/api/agent-registry/address/0x0000000000000000000000000000000000000000"
        )
        assert resp.status_code == 404


class TestUpdateAgentRegistry:
    def test_success(self, db, registry):
        c = make_client(db, auth_agent_id=registry.agent_id)
        resp = c.put(
            f"/api/agent-registry/{registry.agent_id}",
            json={"agent_registry": {"agent_name": "renamed"}},
        )
        assert resp.status_code == 200
        assert resp.json()["agent_name"] == "renamed"

    def test_wrong_owner(self, db, registry):
        c = make_client(db, auth_agent_id=9999)
        resp = c.put(
            f"/api/agent-registry/{registry.agent_id}",
            json={"agent_registry": {"agent_name": "hacked"}},
        )
        assert resp.status_code == 403

    def test_not_found(self, db):
        c = make_client(db, auth_agent_id=9999)
        resp = c.put(
            "/api/agent-registry/9999",
            json={"agent_registry": {"agent_name": "x"}},
        )
        assert resp.status_code == 404


class TestDeleteAgentRegistry:
    def test_success(self, db, registry):
        c = make_client(db, auth_agent_id=registry.agent_id)
        resp = c.delete(f"/api/agent-registry/{registry.agent_id}")
        assert resp.status_code == 200

        resp2 = c.get(f"/api/agent-registry/{registry.agent_id}")
        assert resp2.status_code == 404

    def test_wrong_owner(self, db, registry):
        c = make_client(db, auth_agent_id=9999)
        resp = c.delete(f"/api/agent-registry/{registry.agent_id}")
        assert resp.status_code == 403
