from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from ..db import get_db
from ..dependencies import get_api_key
from ..utils import generate_api_key

router = APIRouter()

@router.post("/api/agents/", response_model=schemas.AgentWithAPIKey)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    db_agent = models.Agent(agent_name=agent.agent_name)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    
    # Generate and store API key for the new agent
    key = generate_api_key()
    db_api_key = models.APIKey(key=key, agent_id=db_agent.agent_id)
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return schemas.AgentWithAPIKey(
        agent_id=db_agent.agent_id,
        agent_name=db_agent.agent_name,
        created_at=db_agent.created_at,
        api_key=db_api_key.key
    )

@router.get("/api/agents/{agent_id}", response_model=schemas.Agent)
def read_agent(agent_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.post("/api/agents/{agent_id}/twitter_accounts/", response_model=schemas.TwitterAccount)
def create_twitter_account(agent_id: int, account: schemas.TwitterAccountCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_account = models.TwitterAccount(
        agent_id=agent_id,
        twitter_handle=account.twitter_handle,
        username=account.username,
        twitter_user_id=account.twitter_user_id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.post("/api/agents/{agent_id}/accounts/{twitter_user_id}/tweets/", response_model=schemas.Tweet)
def create_tweet(agent_id: int, twitter_user_id: str, tweet: schemas.TweetCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_tweet = models.Tweet(
        twitter_user_id=twitter_user_id,
        user_name=tweet.user_name,
        text=tweet.text,
        created_at=tweet.created_at,
        view_count=tweet.view_count,
        retweet_count=tweet.retweet_count,
        quote_count=tweet.quote_count,
        view_count_state=tweet.view_count_state
    )
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)
    return db_tweet

@router.post("/api/agents/{agent_id}/accounts/{twitter_user_id}/tweets/{tweet_id}/interactions/", response_model=schemas.Interaction)
def create_interaction(agent_id: int, twitter_user_id: str, tweet_id: int, interaction: schemas.InteractionCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_interaction = models.Interaction(tweet_id=tweet_id, agent_id=agent_id, interaction_type=interaction.interaction_type)
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

@router.get("/api/tweets/{tweet_id}", response_model=schemas.Tweet)
def read_tweet(tweet_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_tweet = db.query(models.Tweet).filter(models.Tweet.tweet_id == tweet_id).first()
    if db_tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")
    return db_tweet