from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum

class InteractionType(str, Enum):
    like = "like"
    retweet = "retweet"
    reply = "reply"
    quote_tweet = "quote_tweet"
    follow = "follow"

class AgentBase(BaseModel):
    agent_name: str

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AgentWithAPIKey(Agent):
    api_key: str

    class Config:
        from_attributes = True

class TwitterAccountBase(BaseModel):
    username: str 
    name: str  
    twitter_user_id: str

class TwitterAccountCreate(TwitterAccountBase):
    pass

class TwitterAccount(TwitterAccountBase):
    created_at: datetime

    class Config:
        from_attributes = True

class TweetBase(BaseModel):
    user_name: str
    text: str
    created_at: datetime

class TweetCreate(TweetBase):
    tweet_id: Optional[int] = None

class Tweet(TweetBase):
    tweet_id: int
    twitter_user_id: Optional[str] = None  

    class Config:
        from_attributes = True

class InteractionBase(BaseModel):
    interaction_type: InteractionType

class InteractionCreate(InteractionBase):
    tweet_id: Optional[int] = None  
    user_id: Optional[str] = None  

class Interaction(InteractionBase):
    interaction_id: int
    tweet_id: Optional[int] = None  
    user_id: Optional[str] = None  
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class APIKeyBase(BaseModel):
    agent_id: int

class APIKeyCreate(APIKeyBase):
    pass

class APIKey(APIKeyBase):
    id: int
    key: str
    created_at: datetime

    class Config:
        from_attributes = True

class AgentTypeBase(BaseModel):
    type_name: str
    description: str

class AgentTypeCreate(AgentTypeBase):
    pass

class AgentTypeUpdate(AgentTypeBase):
    pass

class AgentType(AgentTypeBase):
    type_id: int

    class Config:
        from_attributes = True

class AttributeDefinitionBase(BaseModel):
    type_id: int
    attr_name: str
    data_type: str
    is_required: bool
    default_value: Optional[str] = None

class AttributeDefinitionCreate(AttributeDefinitionBase):
    pass

class AttributeDefinitionUpdate(AttributeDefinitionBase):
    pass

class AttributeDefinition(AttributeDefinitionBase):
    attr_def_id: int

    class Config:
        from_attributes = True

class AgentAttributeBase(BaseModel):
    agent_id: int
    attr_def_id: int
    string_value: Optional[str] = None
    integer_value: Optional[int] = None
    float_value: Optional[float] = None
    boolean_value: Optional[bool] = None
    date_value: Optional[datetime] = None
    json_value: Optional[dict] = None

class AgentAttributeCreate(AgentAttributeBase):
    pass

class AgentAttributeUpdate(AgentAttributeBase):
    pass

class AgentAttribute(AgentAttributeBase):
    attribute_id: int
    last_updated: datetime

    class Config:
        from_attributes = True

class AgentRegistryBase(BaseModel):
    agent_name: str
    type_id: int
    eth_address: str  # Ethereum address for authentication

class AgentRegistryCreate(AgentRegistryBase):
    pass

class AgentRegistryUpdate(BaseModel):
    agent_name: Optional[str] = None
    type_id: Optional[int] = None
    eth_address: Optional[str] = None

class AgentRegistry(AgentRegistryBase):
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentAddressBase(BaseModel):
    agent_id: int
    eth_address: str

class AgentAddressUpdate(BaseModel):
    is_active: bool

class AgentAddress(AgentAddressBase):
    address_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class SignatureAuth(BaseModel):
    agent_id: int
    signature: str
    message: str
