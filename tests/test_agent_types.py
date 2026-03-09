from app.models.models import AgentType


class TestCreateAgentType:
    def test_success(self, client):
        resp = client.post(
            "/api/agent-types/",
            json={"type_name": "Chatbot", "description": "A chat agent"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["type_name"] == "Chatbot"
        assert "type_id" in data


class TestReadAgentTypes:
    def test_list(self, client, agent_type):
        resp = client.get("/api/agent-types/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_pagination(self, client, db):
        for i in range(5):
            db.add(AgentType(type_name=f"type_{i}", description=f"desc {i}"))
        db.commit()

        resp = client.get("/api/agent-types/?skip=2&limit=2")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_by_id(self, client, agent_type):
        resp = client.get(f"/api/agent-types/{agent_type.type_id}")
        assert resp.status_code == 200
        assert resp.json()["type_name"] == "TestBot"

    def test_by_id_not_found(self, client):
        resp = client.get("/api/agent-types/9999")
        assert resp.status_code == 404

    def test_by_name_case_insensitive(self, client, agent_type):
        resp = client.get("/api/agent-types/name/testbot")
        assert resp.status_code == 200
        assert resp.json()["type_name"] == "TestBot"

        resp2 = client.get("/api/agent-types/name/TESTBOT")
        assert resp2.status_code == 200

    def test_by_name_not_found(self, client):
        resp = client.get("/api/agent-types/name/nonexistent")
        assert resp.status_code == 404


class TestUpdateAgentType:
    def test_success(self, client, agent_type):
        resp = client.put(
            f"/api/agent-types/{agent_type.type_id}",
            json={
                "agent_type": {"type_name": "Updated", "description": "Updated desc"}
            },
        )
        assert resp.status_code == 200
        assert resp.json()["type_name"] == "Updated"

    def test_not_found(self, client):
        resp = client.put(
            "/api/agent-types/9999",
            json={"agent_type": {"type_name": "X", "description": "X"}},
        )
        assert resp.status_code == 404


class TestDeleteAgentType:
    def test_success(self, client, agent_type):
        resp = client.delete(f"/api/agent-types/{agent_type.type_id}")
        assert resp.status_code == 200
        assert resp.json()["type_id"] == agent_type.type_id

        # Confirm deletion
        resp2 = client.get(f"/api/agent-types/{agent_type.type_id}")
        assert resp2.status_code == 404

    def test_not_found(self, client):
        resp = client.delete("/api/agent-types/9999")
        assert resp.status_code == 404


class TestGetAgentsByType:
    def test_success(self, client, registry):
        resp = client.get(f"/api/agent-types/{registry.type_id}/agents/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_empty(self, client, agent_type):
        resp = client.get(f"/api/agent-types/{agent_type.type_id}/agents/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_type_not_found(self, client):
        resp = client.get("/api/agent-types/9999/agents/")
        assert resp.status_code == 404
