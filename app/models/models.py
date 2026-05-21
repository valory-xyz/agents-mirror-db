"""SQLAlchemy ORM model definitions and the shared `Base` declarative class."""

import datetime
import enum

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Declarative base class for every ORM model in this module."""


class InteractionType(enum.Enum):
    """Allowed values for `Interaction.interaction_type`."""

    like = "like"
    retweet = "retweet"
    reply = "reply"
    quote_tweet = "quote_tweet"
    follow = "follow"


class Agent(Base):
    """An agent that owns one or more Twitter accounts and API keys."""

    __tablename__ = "agents"
    agent_id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    api_keys = relationship("APIKey", back_populates="agent")


class TwitterAccount(Base):
    """A Twitter account owned by an `Agent`."""

    __tablename__ = "twitter_accounts"
    twitter_user_id = Column(String, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id"))
    username = Column(String, index=True)
    name = Column(String)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    agent = relationship("Agent", back_populates="twitter_accounts")


class Tweet(Base):
    """A tweet authored from a `TwitterAccount`."""

    __tablename__ = "tweets"
    tweet_id = Column(BigInteger, primary_key=True, index=True)
    twitter_user_id = Column(
        String, ForeignKey("twitter_accounts.twitter_user_id"), nullable=True
    )
    user_name = Column(String)
    text = Column(String)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    account = relationship("TwitterAccount", back_populates="tweets")
    interactions = relationship(
        "Interaction", order_by="Interaction.interaction_id", back_populates="tweet"
    )


class Interaction(Base):
    """An action (like, retweet, reply, quote, follow) recorded against an agent."""

    __tablename__ = "interactions"
    interaction_id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(BigInteger, ForeignKey("tweets.tweet_id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id"))
    user_id = Column(String, ForeignKey("twitter_accounts.twitter_user_id"))
    interaction_type = Column(Enum(InteractionType))
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    tweet = relationship("Tweet", back_populates="interactions")
    agent = relationship("Agent", back_populates="interactions")


class APIKey(Base):
    """An API key bound to a single `Agent` used to authorize protected endpoints."""

    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.agent_id"))
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    agent = relationship("Agent", back_populates="api_keys")


class AgentType(Base):
    """Schema definition for a family of agents (e.g. trader, oracle)."""

    __tablename__ = "agent_types"

    type_id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String, index=True)
    description = Column(String)

    attribute_definitions = relationship(
        "AttributeDefinition", back_populates="agent_type"
    )
    agent_registries = relationship("AgentRegistry", back_populates="agent_type")


class AttributeDefinition(Base):
    """Declares a typed attribute that agents of a given `AgentType` carry."""

    __tablename__ = "attribute_definitions"

    attr_def_id = Column(Integer, primary_key=True, index=True)
    type_id = Column(Integer, ForeignKey("agent_types.type_id"))
    attr_name = Column(String, index=True)
    data_type = Column(String)
    is_required = Column(Boolean, default=False)
    default_value = Column(String, nullable=True)

    agent_type = relationship("AgentType", back_populates="attribute_definitions")
    agent_attributes = relationship(
        "AgentAttribute", back_populates="attribute_definition"
    )


class AgentAttribute(Base):
    """A typed value for one `AttributeDefinition` on one registered agent."""

    __tablename__ = "agent_attributes"

    attribute_id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agent_registry.agent_id"))
    attr_def_id = Column(Integer, ForeignKey("attribute_definitions.attr_def_id"))
    string_value = Column(String, nullable=True)
    integer_value = Column(Integer, nullable=True)
    float_value = Column(Float, nullable=True)
    boolean_value = Column(Boolean, nullable=True)
    date_value = Column(DateTime, nullable=True)
    json_value = Column(JSON, nullable=True)
    last_updated = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    agent_registry = relationship("AgentRegistry", back_populates="agent_attributes")
    attribute_definition = relationship(
        "AttributeDefinition", back_populates="agent_attributes"
    )


class AgentRegistry(Base):
    """Registry entry binding an agent ID to an Ethereum address and `AgentType`."""

    __tablename__ = "agent_registry"

    agent_id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    type_id = Column(Integer, ForeignKey("agent_types.type_id"))
    eth_address = Column(String, index=True, unique=True)
    created_at = Column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    agent_type = relationship("AgentType", back_populates="agent_registries")
    agent_attributes = relationship("AgentAttribute", back_populates="agent_registry")


# Define relationships
Agent.twitter_accounts = relationship(
    "TwitterAccount", order_by=TwitterAccount.twitter_user_id, back_populates="agent"
)
TwitterAccount.tweets = relationship(
    "Tweet", order_by=Tweet.tweet_id, back_populates="account"
)
Tweet.interactions = relationship(
    "Interaction", order_by=Interaction.interaction_id, back_populates="tweet"
)
Agent.interactions = relationship(
    "Interaction", order_by=Interaction.interaction_id, back_populates="agent"
)
