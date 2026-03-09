from app.models.models import AgentAttribute, AgentRegistry
from tests.conftest import make_client


class TestCreateAgentAttribute:
    def test_success(self, db, registry, attr_def):
        c = make_client(db, auth_agent_id=registry.agent_id)
        resp = c.post(
            f"/api/agents/{registry.agent_id}/attributes/",
            json={
                "agent_attr": {
                    "agent_id": registry.agent_id,
                    "attr_def_id": attr_def.attr_def_id,
                    "string_value": "friendly",
                }
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["string_value"] == "friendly"
        assert data["agent_id"] == registry.agent_id
        assert "attribute_id" in data
        assert "last_updated" in data

    def test_wrong_owner(self, db, registry, attr_def):
        c = make_client(db, auth_agent_id=9999)
        resp = c.post(
            f"/api/agents/{registry.agent_id}/attributes/",
            json={
                "agent_attr": {
                    "agent_id": registry.agent_id,
                    "attr_def_id": attr_def.attr_def_id,
                    "string_value": "hacked",
                }
            },
        )
        assert resp.status_code == 403

    def test_agent_not_found(self, db, attr_def):
        c = make_client(db, auth_agent_id=9999)
        resp = c.post(
            "/api/agents/9999/attributes/",
            json={
                "agent_attr": {
                    "agent_id": 9999,
                    "attr_def_id": attr_def.attr_def_id,
                    "string_value": "x",
                }
            },
        )
        assert resp.status_code == 404

    def test_attr_def_not_found(self, db, registry):
        c = make_client(db, auth_agent_id=registry.agent_id)
        resp = c.post(
            f"/api/agents/{registry.agent_id}/attributes/",
            json={
                "agent_attr": {
                    "agent_id": registry.agent_id,
                    "attr_def_id": 9999,
                    "string_value": "x",
                }
            },
        )
        assert resp.status_code == 404


class TestReadAgentAttributes:
    def _seed_attribute(self, db, registry, attr_def):
        attr = AgentAttribute(
            agent_id=registry.agent_id,
            attr_def_id=attr_def.attr_def_id,
            string_value="curious",
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)
        return attr

    def test_by_agent(self, client, db, registry, attr_def):
        self._seed_attribute(db, registry, attr_def)
        resp = client.get(f"/api/agents/{registry.agent_id}/attributes/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_by_agent_not_found(self, client):
        resp = client.get("/api/agents/9999/attributes/")
        assert resp.status_code == 404

    def test_all_attributes(self, client, db, registry, attr_def):
        self._seed_attribute(db, registry, attr_def)
        resp = client.get(f"/api/agents/{registry.agent_id}/all-attributes/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_all_attributes_empty(self, client, registry):
        resp = client.get(f"/api/agents/{registry.agent_id}/all-attributes/")
        assert resp.status_code == 404

    def test_by_id(self, client, db, registry, attr_def):
        attr = self._seed_attribute(db, registry, attr_def)
        resp = client.get(f"/api/agent-attributes/{attr.attribute_id}")
        assert resp.status_code == 200
        assert resp.json()["string_value"] == "curious"

    def test_by_id_not_found(self, client):
        resp = client.get("/api/agent-attributes/9999")
        assert resp.status_code == 404

    def test_by_agent_and_def(self, client, db, registry, attr_def):
        self._seed_attribute(db, registry, attr_def)
        resp = client.get(
            f"/api/agents/{registry.agent_id}/attributes/{attr_def.attr_def_id}"
        )
        assert resp.status_code == 200
        assert resp.json()["string_value"] == "curious"

    def test_by_agent_and_def_not_found(self, client, registry):
        resp = client.get(f"/api/agents/{registry.agent_id}/attributes/9999")
        assert resp.status_code == 404


class TestAttributeValuesByType:
    def test_returns_values_across_agents(self, client, db, agent_type, attr_def):
        """Create two agents of the same type with the same attribute."""
        r1 = AgentRegistry(
            agent_name="a1", type_id=agent_type.type_id, eth_address="0x1111"
        )
        r2 = AgentRegistry(
            agent_name="a2", type_id=agent_type.type_id, eth_address="0x2222"
        )
        db.add_all([r1, r2])
        db.commit()
        db.refresh(r1)
        db.refresh(r2)

        a1_attr = AgentAttribute(
            agent_id=r1.agent_id,
            attr_def_id=attr_def.attr_def_id,
            string_value="val1",
        )
        a2_attr = AgentAttribute(
            agent_id=r2.agent_id,
            attr_def_id=attr_def.attr_def_id,
            string_value="val2",
        )
        db.add_all([a1_attr, a2_attr])
        db.commit()

        resp = client.get(
            f"/api/agent-types/{agent_type.type_id}/attributes/{attr_def.attr_def_id}/values"
        )
        assert resp.status_code == 200
        values = resp.json()
        assert len(values) == 2
        string_vals = {v["string_value"] for v in values}
        assert string_vals == {"val1", "val2"}

    def test_type_not_found(self, client, attr_def):
        resp = client.get(
            f"/api/agent-types/9999/attributes/{attr_def.attr_def_id}/values"
        )
        assert resp.status_code == 404

    def test_attr_def_not_found(self, client, agent_type):
        resp = client.get(
            f"/api/agent-types/{agent_type.type_id}/attributes/9999/values"
        )
        assert resp.status_code == 404

    def test_empty_when_no_agents(self, client, agent_type, attr_def):
        resp = client.get(
            f"/api/agent-types/{agent_type.type_id}/attributes/{attr_def.attr_def_id}/values"
        )
        assert resp.status_code == 200
        assert resp.json() == []


class TestUpdateAgentAttribute:
    def test_success(self, db, registry, attr_def):
        attr = AgentAttribute(
            agent_id=registry.agent_id,
            attr_def_id=attr_def.attr_def_id,
            string_value="old",
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)

        c = make_client(db, auth_agent_id=registry.agent_id)
        resp = c.put(
            f"/api/agent-attributes/{attr.attribute_id}",
            json={
                "agent_attr": {
                    "agent_id": registry.agent_id,
                    "attr_def_id": attr_def.attr_def_id,
                    "string_value": "new",
                }
            },
        )
        assert resp.status_code == 200
        assert resp.json()["string_value"] == "new"

    def test_wrong_owner(self, db, registry, attr_def):
        attr = AgentAttribute(
            agent_id=registry.agent_id,
            attr_def_id=attr_def.attr_def_id,
            string_value="safe",
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)

        c = make_client(db, auth_agent_id=9999)
        resp = c.put(
            f"/api/agent-attributes/{attr.attribute_id}",
            json={
                "agent_attr": {
                    "agent_id": registry.agent_id,
                    "attr_def_id": attr_def.attr_def_id,
                    "string_value": "hacked",
                }
            },
        )
        assert resp.status_code == 403

    def test_not_found(self, db):
        c = make_client(db, auth_agent_id=1)
        resp = c.put(
            "/api/agent-attributes/9999",
            json={"agent_attr": {"agent_id": 1, "attr_def_id": 1, "string_value": "x"}},
        )
        assert resp.status_code == 404


class TestDeleteAgentAttribute:
    def test_success(self, db, registry, attr_def):
        attr = AgentAttribute(
            agent_id=registry.agent_id,
            attr_def_id=attr_def.attr_def_id,
            string_value="doomed",
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)

        c = make_client(db, auth_agent_id=registry.agent_id)
        resp = c.delete(f"/api/agent-attributes/{attr.attribute_id}")
        assert resp.status_code == 200

        resp2 = c.get(f"/api/agent-attributes/{attr.attribute_id}")
        assert resp2.status_code == 404

    def test_wrong_owner(self, db, registry, attr_def):
        attr = AgentAttribute(
            agent_id=registry.agent_id,
            attr_def_id=attr_def.attr_def_id,
            string_value="protected",
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)

        c = make_client(db, auth_agent_id=9999)
        resp = c.delete(f"/api/agent-attributes/{attr.attribute_id}")
        assert resp.status_code == 403
