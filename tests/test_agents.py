class TestCreateAgent:
    def test_returns_agent_with_api_key(self, client):
        resp = client.post("/api/agents/", json={"agent_name": "bot1"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["agent_name"] == "bot1"
        assert "agent_id" in data
        assert "api_key" in data
        assert "created_at" in data
        assert len(data["api_key"]) > 20

    def test_two_agents_get_different_keys(self, client):
        r1 = client.post("/api/agents/", json={"agent_name": "a"}).json()
        r2 = client.post("/api/agents/", json={"agent_name": "b"}).json()
        assert r1["api_key"] != r2["api_key"]
        assert r1["agent_id"] != r2["agent_id"]


class TestReadAgent:
    def test_success(self, client, agent):
        resp = client.get(f"/api/agents/{agent.agent_id}")
        assert resp.status_code == 200
        assert resp.json()["agent_name"] == "test-agent"

    def test_not_found(self, client):
        resp = client.get("/api/agents/9999")
        assert resp.status_code == 404
