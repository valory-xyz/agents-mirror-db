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
    return schemas.AgentWithAPIKey(**db_agent.__dict__, api_key=db_api_key.key)

@router.get("/api/agents/{agent_id}", response_model=schemas.Agent)
def read_agent(agent_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.post("/api/agents/{agent_id}/twitter_accounts/", response_model=schemas.TwitterAccount)
def create_twitter_account(agent_id: int, account: schemas.TwitterAccountCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_account = models.TwitterAccount(**account.dict(), agent_id=agent_id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/api/twitter_accounts/{twitter_user_id}", response_model=schemas.TwitterAccount)
def get_twitter_account(twitter_user_id: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_account = db.query(models.TwitterAccount).filter(models.TwitterAccount.twitter_user_id == twitter_user_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Twitter account not found")
    return db_account

@router.post("/api/agents/{agent_id}/accounts/{twitter_user_id}/tweets/", response_model=schemas.Tweet)
def create_tweet(agent_id: int, twitter_user_id: str, tweet: schemas.TweetCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_tweet = models.Tweet(**tweet.dict(), twitter_user_id=twitter_user_id)
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)
    return db_tweet

@router.post("/api/agents/{agent_id}/accounts/{twitter_user_id}/tweets/{tweet_id}/interactions/", response_model=schemas.Interaction)
def create_interaction(agent_id: int, twitter_user_id: str, tweet_id: int, interaction: schemas.InteractionCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    # Check if the tweet exists
    db_tweet = db.query(models.Tweet).filter(models.Tweet.tweet_id == tweet_id).first()
    if db_tweet is None:
        raise HTTPException(status_code=404, detail="Tweet not found")
    
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

@router.get("/api/interactions/{interaction_id}", response_model=schemas.Interaction)
def read_interaction(interaction_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_interaction = db.query(models.Interaction).filter(models.Interaction.interaction_id == interaction_id).first()
    if db_interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction