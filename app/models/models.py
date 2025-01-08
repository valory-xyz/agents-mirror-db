from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import datetime

Base = declarative_base()

class InteractionType(enum.Enum):
    like = "like"
    retweet = "retweet"
    reply = "reply"
    quote_tweet = "quote_tweet"
    follow = "follow"

class Agent(Base):
    __tablename__ = 'agents'
    agent_id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    api_keys = relationship("APIKey", back_populates="agent")

class TwitterAccount(Base):
    __tablename__ = 'twitter_accounts'
    twitter_user_id = Column(String, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.agent_id'))
    twitter_handle = Column(String, index=True)
    username = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    agent = relationship("Agent", back_populates="twitter_accounts")

class Tweet(Base):
    __tablename__ = 'tweets'
    tweet_id = Column(Integer, primary_key=True, index=True)
    twitter_user_id = Column(String, ForeignKey('twitter_accounts.twitter_user_id'))
    user_name = Column(String)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    view_count = Column(Integer)
    retweet_count = Column(Integer)
    quote_count = Column(Integer)
    view_count_state = Column(String)
    account = relationship("TwitterAccount", back_populates="tweets")

class Interaction(Base):
    __tablename__ = 'interactions'
    interaction_id = Column(Integer, primary_key=True, index=True)
    tweet_id = Column(Integer, ForeignKey('tweets.tweet_id'))
    agent_id = Column(Integer, ForeignKey('agents.agent_id'))
    interaction_type = Column(Enum(InteractionType))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    tweet = relationship("Tweet", back_populates="interactions")
    agent = relationship("Agent", back_populates="interactions")

class APIKey(Base):
    __tablename__ = 'api_keys'
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    agent_id = Column(Integer, ForeignKey('agents.agent_id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    agent = relationship("Agent", back_populates="api_keys")

Agent.twitter_accounts = relationship("TwitterAccount", order_by=TwitterAccount.twitter_user_id, back_populates="agent")
TwitterAccount.tweets = relationship("Tweet", order_by=Tweet.tweet_id, back_populates="account")
Tweet.interactions = relationship("Interaction", order_by=Interaction.interaction_id, back_populates="tweet")
Agent.interactions = relationship("Interaction", order_by=Interaction.interaction_id, back_populates="agent")