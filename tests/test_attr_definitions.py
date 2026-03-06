class TestCreateAttributeDefinition:
    def test_success(self, client, agent_type):
        resp = client.post(
            f"/api/agent-types/{agent_type.type_id}/attributes/",
            json={
                "attr_def": {
                    "type_id": agent_type.type_id,
                    "attr_name": "mood",
                    "data_type": "string",
                    "is_required": False,
                    "default_value": "neutral",
                }
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["attr_name"] == "mood"
        assert data["default_value"] == "neutral"
        assert "attr_def_id" in data

    def test_type_not_found(self, client):
        resp = client.post(
            "/api/agent-types/9999/attributes/",
            json={
                "attr_def": {
                    "type_id": 9999,
                    "attr_name": "x",
                    "data_type": "string",
                    "is_required": False,
                }
            },
        )
        assert resp.status_code == 404


class TestReadAttributeDefinitions:
    def test_by_type(self, client, attr_def, agent_type):
        resp = client.get(f"/api/agent-types/{agent_type.type_id}/attributes/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["attr_name"] == "personality"

    def test_by_type_not_found(self, client):
        resp = client.get("/api/agent-types/9999/attributes/")
        assert resp.status_code == 404

    def test_by_id(self, client, attr_def):
        resp = client.get(f"/api/attributes/{attr_def.attr_def_id}")
        assert resp.status_code == 200
        assert resp.json()["attr_name"] == "personality"

    def test_by_id_not_found(self, client):
        resp = client.get("/api/attributes/9999")
        assert resp.status_code == 404

    def test_by_name_case_insensitive(self, client, attr_def):
        resp = client.get("/api/attributes/name/PERSONALITY")
        assert resp.status_code == 200
        assert resp.json()["attr_name"] == "personality"

    def test_by_name_not_found(self, client):
        resp = client.get("/api/attributes/name/nonexistent")
        assert resp.status_code == 404


class TestUpdateAttributeDefinition:
    def test_success(self, client, attr_def, agent_type):
        resp = client.put(
            f"/api/attributes/{attr_def.attr_def_id}",
            json={
                "attr_def": {
                    "type_id": agent_type.type_id,
                    "attr_name": "updated_name",
                    "data_type": "integer",
                    "is_required": True,
                }
            },
        )
        assert resp.status_code == 200
        assert resp.json()["attr_name"] == "updated_name"
        assert resp.json()["data_type"] == "integer"

    def test_not_found(self, client):
        resp = client.put(
            "/api/attributes/9999",
            json={
                "attr_def": {
                    "type_id": 1,
                    "attr_name": "x",
                    "data_type": "string",
                    "is_required": False,
                }
            },
        )
        assert resp.status_code == 404


class TestDeleteAttributeDefinition:
    def test_success(self, client, attr_def):
        resp = client.delete(f"/api/attributes/{attr_def.attr_def_id}")
        assert resp.status_code == 200

        resp2 = client.get(f"/api/attributes/{attr_def.attr_def_id}")
        assert resp2.status_code == 404

    def test_not_found(self, client):
        resp = client.delete("/api/attributes/9999")
        assert resp.status_code == 404
