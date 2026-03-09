from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.schemas import (
    AgentAttributeCreate,
    AgentCreate,
    AgentRegistryCreate,
    AgentRegistryUpdate,
    InteractionCreate,
    InteractionType,
    SignatureAuth,
    TweetCreate,
)


class TestAgentCreate:
    def test_valid(self):
        s = AgentCreate(agent_name="bot1")
        assert s.agent_name == "bot1"

    def test_missing_name(self):
        with pytest.raises(ValidationError):
            AgentCreate()


class TestInteractionCreate:
    def test_valid_enum(self):
        ic = InteractionCreate(interaction_type=InteractionType.like, tweet_id=1)
        assert ic.interaction_type == InteractionType.like

    def test_invalid_enum(self):
        with pytest.raises(ValidationError):
            InteractionCreate(interaction_type="invalid_type")

    def test_optional_fields(self):
        ic = InteractionCreate(interaction_type=InteractionType.follow)
        assert ic.tweet_id is None
        assert ic.user_id is None


class TestTweetCreate:
    def test_optional_tweet_id(self):
        tc = TweetCreate(
            user_name="user", text="hello", created_at=datetime.now(), tweet_id=None
        )
        assert tc.tweet_id is None

    def test_with_tweet_id(self):
        tc = TweetCreate(
            user_name="user", text="hello", created_at=datetime.now(), tweet_id=12345
        )
        assert tc.tweet_id == 12345


class TestAgentRegistryCreate:
    def test_requires_all_fields(self):
        s = AgentRegistryCreate(agent_name="bot", type_id=1, eth_address="0xabc")
        assert s.eth_address == "0xabc"

    def test_missing_eth_address(self):
        with pytest.raises(ValidationError):
            AgentRegistryCreate(agent_name="bot", type_id=1)


class TestAgentRegistryUpdate:
    def test_all_optional(self):
        s = AgentRegistryUpdate()
        assert s.agent_name is None
        assert s.type_id is None
        assert s.eth_address is None

    def test_partial_update(self):
        s = AgentRegistryUpdate(agent_name="new-name")
        assert s.agent_name == "new-name"
        assert s.type_id is None


class TestSignatureAuth:
    def test_requires_all_fields(self):
        s = SignatureAuth(agent_id=1, signature="0xabc", message="hello")
        assert s.agent_id == 1

    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            SignatureAuth(agent_id=1)


class TestAgentAttributeCreate:
    def test_value_fields_optional(self):
        s = AgentAttributeCreate(agent_id=1, attr_def_id=1)
        assert s.string_value is None
        assert s.integer_value is None
        assert s.json_value is None

    def test_with_values(self):
        s = AgentAttributeCreate(
            agent_id=1,
            attr_def_id=1,
            string_value="hello",
            integer_value=42,
            json_value={"key": "val"},
        )
        assert s.string_value == "hello"
        assert s.integer_value == 42
