"""Pydantic request and response schemas for the FastAPI router."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InteractionType(str, Enum):
    """Allowed values for `InteractionCreate.interaction_type`."""

    like = "like"
    retweet = "retweet"
    reply = "reply"
    quote_tweet = "quote_tweet"
    follow = "follow"


class AgentBase(BaseModel):
    """Shared fields for agent request and response shapes."""

    agent_name: str


class AgentCreate(AgentBase):
    """Request body for POST /agents/."""


class Agent(AgentBase):
    """Agent response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    agent_id: int
    created_at: datetime


class AgentWithAPIKey(Agent):
    """Agent response that also includes the freshly minted API key."""

    api_key: str


class TwitterAccountBase(BaseModel):
    """Shared fields for Twitter account request and response shapes."""

    username: str
    name: str
    twitter_user_id: str


class TwitterAccountCreate(TwitterAccountBase):
    """Request body for POST /agents/{agent_id}/twitter_accounts/."""


class TwitterAccount(TwitterAccountBase):
    """Twitter account response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    created_at: datetime


class TweetBase(BaseModel):
    """Shared fields for tweet request and response shapes."""

    user_name: str
    text: str
    created_at: datetime


class TweetCreate(TweetBase):
    """Request body for POST /agents/{agent_id}/accounts/{twitter_user_id}/tweets/."""

    tweet_id: Optional[int] = None


class Tweet(TweetBase):
    """Tweet response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    tweet_id: int
    twitter_user_id: Optional[str] = None


class InteractionBase(BaseModel):
    """Shared field for interaction request and response shapes."""

    interaction_type: InteractionType


class InteractionCreate(InteractionBase):
    """Request body for POST /agents/{agent_id}/accounts/{twitter_user_id}/interactions/."""

    tweet_id: Optional[int] = None
    user_id: Optional[str] = None


class Interaction(InteractionBase):
    """Interaction response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    interaction_id: int
    tweet_id: Optional[int] = None
    user_id: Optional[str] = None
    agent_id: int
    created_at: datetime


class APIKeyBase(BaseModel):
    """Shared field for API key shapes."""

    agent_id: int


class APIKeyCreate(APIKeyBase):
    """Request body for creating an API key."""


class APIKey(APIKeyBase):
    """API key response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    created_at: datetime


class AgentTypeBase(BaseModel):
    """Shared fields for agent type request and response shapes."""

    type_name: str
    description: str


class AgentTypeCreate(AgentTypeBase):
    """Request body for POST /agent-types/."""


class AgentTypeUpdate(AgentTypeBase):
    """Request body for PUT /agent-types/{type_id}."""


class AgentType(AgentTypeBase):
    """Agent type response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    type_id: int


class AttributeDefinitionBase(BaseModel):
    """Shared fields for attribute definition request and response shapes."""

    type_id: int
    attr_name: str
    data_type: str
    is_required: bool
    default_value: Optional[str] = None


class AttributeDefinitionCreate(AttributeDefinitionBase):
    """Request body for POST /attribute-definitions/."""


class AttributeDefinitionUpdate(AttributeDefinitionBase):
    """Request body for PUT /attributes/{attr_def_id}."""


class AttributeDefinition(AttributeDefinitionBase):
    """Attribute definition response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    attr_def_id: int


class AgentAttributeBase(BaseModel):
    """Shared fields for agent attribute value shapes."""

    agent_id: int
    attr_def_id: int
    string_value: Optional[str] = None
    integer_value: Optional[int] = None
    float_value: Optional[float] = None
    boolean_value: Optional[bool] = None
    date_value: Optional[datetime] = None
    json_value: Optional[dict] = None


class AgentAttributeCreate(AgentAttributeBase):
    """Request body for creating an agent attribute value."""


class AgentAttributeUpdate(AgentAttributeBase):
    """Request body for updating an agent attribute value."""


class AgentAttribute(AgentAttributeBase):
    """Agent attribute response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    attribute_id: int
    last_updated: datetime


class AgentRegistryBase(BaseModel):
    """Shared fields for agent registry request and response shapes."""

    agent_name: str
    type_id: int
    eth_address: str  # Ethereum address for authentication


class AgentRegistryCreate(AgentRegistryBase):
    """Request body for POST /agent-registry/."""


class AgentRegistryUpdate(BaseModel):
    """Partial update body for the agent registry entry."""

    agent_name: Optional[str] = None
    type_id: Optional[int] = None
    eth_address: Optional[str] = None


class AgentRegistry(AgentRegistryBase):
    """Agent registry response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    agent_id: int
    created_at: datetime


class AgentAddressBase(BaseModel):
    """Shared fields for agent address shapes."""

    agent_id: int
    eth_address: str


class AgentAddressUpdate(BaseModel):
    """Partial update body to toggle an agent address's active state."""

    is_active: bool


class AgentAddress(AgentAddressBase):
    """Agent address response, populated from the ORM model."""

    model_config = ConfigDict(from_attributes=True)

    address_id: int
    is_active: bool
    created_at: datetime


class SignatureAuth(BaseModel):
    """Request body carrying an ECDSA signature for agent-bound endpoints."""

    agent_id: int
    signature: str
    message: str
