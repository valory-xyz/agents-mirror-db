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