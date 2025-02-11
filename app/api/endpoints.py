import datetime
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from ..models import models
from ..schemas import schemas
from ..db import get_db
from ..dependencies import get_api_key
from ..utils import generate_api_key
from ..models.models import InteractionType
from collections import defaultdict

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
    # Check if a Twitter account with the provided twitter_user_id already exists
    existing_account = db.query(models.TwitterAccount).filter(models.TwitterAccount.twitter_user_id == account.twitter_user_id).first()
    if existing_account:
        raise HTTPException(status_code=409, detail="Twitter account with this twitter_user_id already exists")
    
    db_account = models.TwitterAccount(
        agent_id=agent_id,
        username=account.username,  # Changed from twitter_handle to username
        name=account.name,  # Changed from username to name
        twitter_user_id=account.twitter_user_id
    )
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
    if not tweet.tweet_id:
        raise HTTPException(status_code=400, detail="tweet_id is required")
    
    db_tweet = models.Tweet(
        tweet_id=tweet.tweet_id, 
        twitter_user_id=twitter_user_id,
        user_name=tweet.user_name,
        text=tweet.text,
        created_at=tweet.created_at
    )
    db.add(db_tweet)
    db.commit()
    db.refresh(db_tweet)
    return db_tweet

@router.post("/api/agents/{agent_id}/accounts/{twitter_user_id}/interactions/", response_model=schemas.Interaction)
def create_interaction(agent_id: int, twitter_user_id: str, interaction: schemas.InteractionCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if interaction.interaction_type == InteractionType.follow:
        if interaction.user_id is None:
            raise HTTPException(status_code=400, detail="user_id is required for follow interactions")
    else:
        if interaction.tweet_id is None:
            raise HTTPException(status_code=400, detail="tweet_id is required for non-follow interactions")

    if interaction.tweet_id is not None:
        db_tweet = db.query(models.Tweet).filter(models.Tweet.tweet_id == interaction.tweet_id).first()
        if db_tweet is None:
            db_tweet = models.Tweet(
                tweet_id=interaction.tweet_id,
                twitter_user_id=None,
                user_name="unknown",
                text="",
                created_at=datetime.datetime.utcnow()
            )
            db.add(db_tweet)
            db.commit()
            db.refresh(db_tweet)

    db_interaction = models.Interaction(
        tweet_id=interaction.tweet_id,
        user_id=interaction.user_id,
        agent_id=agent_id,
        interaction_type=interaction.interaction_type
    )
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
def get_interaction(interaction_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_interaction = db.query(models.Interaction).filter(models.Interaction.interaction_id == interaction_id).first()
    if db_interaction is None:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction

@router.get("/api/twitter_accounts/{twitter_user_id}/interactions/", response_model=List[schemas.Interaction])
def get_interactions_by_twitter_user_id(twitter_user_id: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_interactions = db.query(models.Interaction).join(models.Tweet).filter(models.Tweet.twitter_user_id == twitter_user_id).all()
    if not db_interactions:
        raise HTTPException(status_code=404, detail="No interactions found for this Twitter user ID")
    return db_interactions

@router.get("/api/agents/{agent_id}/twitter_accounts/", response_model=List[schemas.TwitterAccount])
def get_twitter_accounts(agent_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_twitter_accounts = db.query(models.TwitterAccount).filter(models.TwitterAccount.agent_id == agent_id).all()
    if not db_twitter_accounts:
        raise HTTPException(status_code=404, detail="No Twitter accounts found for this agent ID")
    return db_twitter_accounts

@router.get("/api/agents/{agent_id}/twitter_accounts/tweets/", response_model=List[schemas.Tweet])
def get_latest_tweets_by_agent_id(agent_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_twitter_accounts = db.query(models.TwitterAccount).filter(models.TwitterAccount.agent_id == agent_id).all()
    if not db_twitter_accounts:
        raise HTTPException(status_code=404, detail="No Twitter accounts found for this agent ID")

    twitter_user_ids = [account.twitter_user_id for account in db_twitter_accounts]
    db_tweets = db.query(models.Tweet).filter(models.Tweet.twitter_user_id.in_(twitter_user_ids)).order_by(models.Tweet.created_at.desc()).limit(20).all()
    
    if not db_tweets:
        raise HTTPException(status_code=404, detail="No tweets found for the associated Twitter accounts")

    return db_tweets

@router.get("/api/agents/{agent_id}/interactions/", response_model=List[schemas.Interaction])
def get_interactions_by_agent_id(agent_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_interactions = db.query(models.Interaction).filter(models.Interaction.agent_id == agent_id).all()
    if not db_interactions:
        raise HTTPException(status_code=404, detail="No interactions found for this agent ID")
    return db_interactions

@router.get("/api/active_usernames/", response_model=List[str])
def get_active_usernames(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_twitter_accounts = db.query(models.TwitterAccount).order_by(models.TwitterAccount.created_at.desc()).all()
    if not db_twitter_accounts:
        raise HTTPException(status_code=404, detail="No Twitter accounts found")

    # Use a dictionary to store the most recent username for each agent
    agent_usernames = defaultdict(list)
    for account in db_twitter_accounts:
        agent_usernames[account.agent_id].append(account.username)

    # Extract the most recent username for each agent
    active_usernames = [usernames[0] for usernames in agent_usernames.values()]
    return active_usernames

@router.get("/api/twitter_accounts/{twitter_user_id}", response_model=schemas.TwitterAccount)
def get_twitter_account(twitter_user_id: str, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_account = db.query(models.TwitterAccount).filter(models.TwitterAccount.twitter_user_id == twitter_user_id).first()
    if db_account is None:
        raise HTTPException(status_code=404, detail="Twitter account not found")
    return db_account

@router.get("/api/active_twitter_accounts/", response_model=List[schemas.TwitterAccount])
def get_active_twitter_accounts(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_twitter_accounts = db.query(models.TwitterAccount).order_by(models.TwitterAccount.created_at.desc()).all()
    if not db_twitter_accounts:
        raise HTTPException(status_code=404, detail="No Twitter accounts found")

    # Use a dictionary to store the most recent account for each agent
    agent_accounts: Dict[int, schemas.TwitterAccount] = {}
    for account in db_twitter_accounts:
        if account.agent_id not in agent_accounts:
            agent_accounts[account.agent_id] = account

    # Extract the most recent account for each agent
    active_accounts = list(agent_accounts.values())
    return active_accounts
