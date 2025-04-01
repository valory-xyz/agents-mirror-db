import datetime
from datetime import timezone
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from ..models import models
from ..schemas import schemas
from ..db import get_db
from ..dependencies import get_api_key, verify_agent_signature
from ..utils import generate_api_key
from ..models.models import InteractionType
from collections import defaultdict
from sqlalchemy import func
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

    # Get current date and calculate the date 7 days ago
    current_date = datetime.datetime.now(timezone.utc)
    seven_days_ago = current_date - datetime.timedelta(days=7)

    # Use a dictionary to store the most recent account for each agent
    agent_accounts: Dict[int, models.TwitterAccount] = {}
    active_accounts = []

    for account in db_twitter_accounts:
        # Skip if we already have a more recent account for this agent
        if account.agent_id in agent_accounts:
            continue

        # Check for tweets in the last 7 days
        recent_tweets = (
            db.query(models.Tweet)
            .filter(
                models.Tweet.twitter_user_id == account.twitter_user_id,
                models.Tweet.created_at >= seven_days_ago,
            )
            .first()
        )

        # Check if the agent associated with this account had ANY interactions (including follows) in the last 7 days
        recent_agent_interactions = (
            db.query(models.Interaction)
            .filter(
                models.Interaction.agent_id
                == account.agent_id,  # Filter by the agent performing the interaction
                models.Interaction.created_at >= seven_days_ago,  # Filter by time
            )
            .first()  # We only need to know if at least one exists
        )

        # If there have been recent tweets OR recent interactions by the agent, add this account
        if recent_tweets or recent_agent_interactions:
            agent_accounts[account.agent_id] = account
            active_accounts.append(account)

    if not active_accounts:
        raise HTTPException(
            status_code=404,
            detail="No active Twitter accounts found in the last 7 days",
        )

    return active_accounts

# No more Agent Address management endpoints as eth_address is now part of AgentRegistry

# AgentType CRUD operations
@router.post("/api/agent-types/", response_model=schemas.AgentType)
def create_agent_type(
    agent_type: schemas.AgentTypeCreate,
    db: Session = Depends(get_db)
):

    db_agent_type = models.AgentType(
        type_name=agent_type.type_name,
        description=agent_type.description
    )
    db.add(db_agent_type)
    db.commit()
    db.refresh(db_agent_type)
    return db_agent_type

@router.get("/api/agent-types/", response_model=List[schemas.AgentType])
def read_agent_types(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    agent_types = db.query(models.AgentType).offset(skip).limit(limit).all()
    return agent_types

@router.get("/api/agent-types/name/{type_name}", response_model=schemas.AgentType)
def read_agent_type_by_name(type_name: str, db: Session = Depends(get_db)):
    db_agent_type = db.query(models.AgentType).filter(func.lower(models.AgentType.type_name) == type_name.lower()).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    return db_agent_type

@router.get("/api/attributes/name/{attr_name}", response_model=schemas.AttributeDefinition)
def read_attribute_definition_by_name(attr_name: str, db: Session = Depends(get_db)):
    db_attr_def = db.query(models.AttributeDefinition).filter(func.lower(models.AttributeDefinition.attr_name) == attr_name.lower()).first()
    if db_attr_def is None:
        raise HTTPException(status_code=404, detail="Attribute definition not found")
    return db_attr_def

@router.get("/api/agents/{agent_id}/attributes/{attr_def_id}", response_model=schemas.AgentAttribute)
def read_agent_attribute_by_agent_and_def(agent_id: int, attr_def_id: int, db: Session = Depends(get_db)):
    db_agent_attr = db.query(models.AgentAttribute).filter(
        models.AgentAttribute.agent_id == agent_id,
        models.AgentAttribute.attr_def_id == attr_def_id
    ).first()
    if db_agent_attr is None:
        raise HTTPException(status_code=404, detail="Agent attribute not found")
    return db_agent_attr

@router.get("/api/agents/{agent_id}/all-attributes/", response_model=List[schemas.AgentAttribute])
def read_all_attributes_of_agent(agent_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    # Verify agent exists in AgentRegistry
    db_agent = db.query(models.AgentRegistry).filter(models.AgentRegistry.agent_id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get all attributes for the agent
    agent_attributes = db.query(models.AgentAttribute).filter(
        models.AgentAttribute.agent_id == agent_id
    ).all()
    
    if not agent_attributes:
        raise HTTPException(status_code=404, detail="No attributes found for this agent ID")
    
    return agent_attributes

@router.get("/api/agent-types/{type_id}", response_model=schemas.AgentType)
def read_agent_type(type_id: int, db: Session = Depends(get_db)):
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    return db_agent_type

@router.put("/api/agent-types/{type_id}", response_model=schemas.AgentType)
def update_agent_type(type_id: int, agent_type: schemas.AgentTypeUpdate, db: Session = Depends(get_db), agent_id: int = Depends(verify_agent_signature)):
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    for key, value in agent_type.dict().items():
        setattr(db_agent_type, key, value)
    
    db.commit()
    db.refresh(db_agent_type)
    return db_agent_type

@router.delete("/api/agent-types/{type_id}", response_model=schemas.AgentType)
def delete_agent_type(type_id: int, db: Session = Depends(get_db), agent_id: int = Depends(verify_agent_signature)):
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    db.delete(db_agent_type)
    db.commit()
    return db_agent_type

# AttributeDefinition CRUD operations
@router.post("/api/agent-types/{type_id}/attributes/", response_model=schemas.AttributeDefinition)
def create_attribute_definition(
    type_id: int, 
    attr_def: schemas.AttributeDefinitionCreate, 
    db: Session = Depends(get_db), 
    agent_id: int = Depends(verify_agent_signature)
):
    # Verify agent type exists
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    # Create attribute definition
    db_attr_def = models.AttributeDefinition(
        type_id=type_id,
        attr_name=attr_def.attr_name,
        data_type=attr_def.data_type,
        is_required=attr_def.is_required,
        default_value=attr_def.default_value
    )
    db.add(db_attr_def)
    db.commit()
    db.refresh(db_attr_def)
    return db_attr_def

@router.get("/api/agent-types/{type_id}/attributes/", response_model=List[schemas.AttributeDefinition])
def read_attribute_definitions_by_type(
    type_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    # Verify agent type exists
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    # Get attribute definitions
    attr_defs = db.query(models.AttributeDefinition).filter(
        models.AttributeDefinition.type_id == type_id
    ).offset(skip).limit(limit).all()
    
    return attr_defs

@router.get("/api/attributes/{attr_def_id}", response_model=schemas.AttributeDefinition)
def read_attribute_definition(attr_def_id: int, db: Session = Depends(get_db)):
    db_attr_def = db.query(models.AttributeDefinition).filter(models.AttributeDefinition.attr_def_id == attr_def_id).first()
    if db_attr_def is None:
        raise HTTPException(status_code=404, detail="Attribute definition not found")
    return db_attr_def

@router.put("/api/attributes/{attr_def_id}", response_model=schemas.AttributeDefinition)
def update_attribute_definition(
    attr_def_id: int, 
    attr_def: schemas.AttributeDefinitionUpdate, 
    db: Session = Depends(get_db), 
    agent_id: int = Depends(verify_agent_signature)
):
    db_attr_def = db.query(models.AttributeDefinition).filter(models.AttributeDefinition.attr_def_id == attr_def_id).first()
    if db_attr_def is None:
        raise HTTPException(status_code=404, detail="Attribute definition not found")
    
    for key, value in attr_def.dict().items():
        setattr(db_attr_def, key, value)
    
    db.commit()
    db.refresh(db_attr_def)
    return db_attr_def

@router.delete("/api/attributes/{attr_def_id}", response_model=schemas.AttributeDefinition)
def delete_attribute_definition(attr_def_id: int, db: Session = Depends(get_db), agent_id: int = Depends(verify_agent_signature)):
    db_attr_def = db.query(models.AttributeDefinition).filter(models.AttributeDefinition.attr_def_id == attr_def_id).first()
    if db_attr_def is None:
        raise HTTPException(status_code=404, detail="Attribute definition not found")
    
    db.delete(db_attr_def)
    db.commit()
    return db_attr_def

# AgentRegistry CRUD operations
@router.post("/api/agent-registry/", response_model=schemas.AgentRegistry)
def create_agent_registry(
    agent_registry: schemas.AgentRegistryCreate, 
    db: Session = Depends(get_db)
):
    # Verify agent type exists
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == agent_registry.type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    # Check if address already exists
    existing_agent = db.query(models.AgentRegistry).filter(
        models.AgentRegistry.eth_address == agent_registry.eth_address
    ).first()
    
    if existing_agent:
        raise HTTPException(status_code=409, detail="Address already registered")
    
    # Create agent registry with eth_address
    db_agent_registry = models.AgentRegistry(
        agent_name=agent_registry.agent_name,
        type_id=agent_registry.type_id,
        eth_address=agent_registry.eth_address
    )
    db.add(db_agent_registry)
    db.commit()
    db.refresh(db_agent_registry)
    
    return db_agent_registry

@router.get("/api/agent-registry/", response_model=List[schemas.AgentRegistry])
def read_agent_registries(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    agent_registries = db.query(models.AgentRegistry).offset(skip).limit(limit).all()
    return agent_registries

@router.get("/api/agent-registry/{agent_id}", response_model=schemas.AgentRegistry)
def read_agent_registry(agent_id: int, db: Session = Depends(get_db)):
    db_agent_registry = db.query(models.AgentRegistry).filter(models.AgentRegistry.agent_id == agent_id).first()
    if db_agent_registry is None:
        raise HTTPException(status_code=404, detail="Agent registry not found")
    return db_agent_registry

@router.get("/api/agent-registry/address/{eth_address}", response_model=schemas.AgentRegistry)
def read_agent_registry_by_address(eth_address: str, db: Session = Depends(get_db)):
    db_agent_registry = db.query(models.AgentRegistry).filter(models.AgentRegistry.eth_address == eth_address).first()
    if db_agent_registry is None:
        raise HTTPException(status_code=404, detail="Agent registry not found")
    return db_agent_registry

@router.put("/api/agent-registry/{agent_id}", response_model=schemas.AgentRegistry)
def update_agent_registry(
    agent_id: int, 
    agent_registry: schemas.AgentRegistryUpdate, 
    db: Session = Depends(get_db), 
    auth_agent_id: int = Depends(verify_agent_signature)
):
    # Verify that the authenticated agent is updating its own data
    if auth_agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this agent")
    
    db_agent_registry = db.query(models.AgentRegistry).filter(models.AgentRegistry.agent_id == agent_id).first()
    if db_agent_registry is None:
        raise HTTPException(status_code=404, detail="Agent registry not found")
    
    for key, value in agent_registry.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_agent_registry, key, value)
    
    db.commit()
    db.refresh(db_agent_registry)
    return db_agent_registry

@router.delete("/api/agent-registry/{agent_id}", response_model=schemas.AgentRegistry)
def delete_agent_registry(agent_id: int, db: Session = Depends(get_db), auth_agent_id: int = Depends(verify_agent_signature)):
    # Verify that the authenticated agent is deleting its own data
    if auth_agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this agent")
    
    db_agent_registry = db.query(models.AgentRegistry).filter(models.AgentRegistry.agent_id == agent_id).first()
    if db_agent_registry is None:
        raise HTTPException(status_code=404, detail="Agent registry not found")
    
    db.delete(db_agent_registry)
    db.commit()
    return db_agent_registry

@router.get("/api/agent-types/{type_id}/agents/", response_model=List[schemas.AgentRegistry])
def read_agents_by_type(
    type_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    # Verify agent type exists
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    # Get agents of this type
    agents = db.query(models.AgentRegistry).filter(
        models.AgentRegistry.type_id == type_id
    ).offset(skip).limit(limit).all()
    
    return agents

# AgentAttribute CRUD operations
@router.post("/api/agents/{agent_id}/attributes/", response_model=schemas.AgentAttribute)
def create_agent_attribute(
    agent_id: int, 
    agent_attr: schemas.AgentAttributeCreate, 
    db: Session = Depends(get_db), 
    auth_agent_id: int = Depends(verify_agent_signature)
):
    print(f"Attempting to create an attribute for agent_id: {agent_id}")
    # Verify that the authenticated agent is creating its own attribute
    if auth_agent_id != agent_id:
        print(f"Authorization failed: auth_agent_id {auth_agent_id} does not match agent_id {agent_id}")
        raise HTTPException(status_code=403, detail="Not authorized to create attributes for this agent")
    
    # Verify agent exists in AgentRegistry
    db_agent = db.query(models.AgentRegistry).filter(models.AgentRegistry.agent_id == agent_id).first()
    if db_agent is None:
        print(f"Agent with agent_id {agent_id} not found in AgentRegistry")
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Verify attribute definition exists
    db_attr_def = db.query(models.AttributeDefinition).filter(models.AttributeDefinition.attr_def_id == agent_attr.attr_def_id).first()
    if db_attr_def is None:
        print(f"Attribute definition with attr_def_id {agent_attr.attr_def_id} not found")
        raise HTTPException(status_code=404, detail="Attribute definition not found")
    
    # Create agent attribute
    db_agent_attr = models.AgentAttribute(
        agent_id=agent_id,
        attr_def_id=agent_attr.attr_def_id,
        string_value=agent_attr.string_value,
        integer_value=agent_attr.integer_value,
        float_value=agent_attr.float_value,
        boolean_value=agent_attr.boolean_value,
        date_value=agent_attr.date_value,
        json_value=agent_attr.json_value
    )
    db.add(db_agent_attr)
    db.commit()
    db.refresh(db_agent_attr)
    print(f"Created agent attribute with attribute_id {db_agent_attr.attribute_id} for agent_id {agent_id}")
    return db_agent_attr

@router.get("/api/agents/{agent_id}/attributes/", response_model=List[schemas.AgentAttribute])
def read_agent_attributes(
    agent_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    # Verify agent exists in AgentRegistry
    db_agent = db.query(models.AgentRegistry).filter(models.AgentRegistry.agent_id == agent_id).first()
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Get agent attributes
    agent_attrs = db.query(models.AgentAttribute).filter(
        models.AgentAttribute.agent_id == agent_id
    ).offset(skip).limit(limit).all()
    
    return agent_attrs

@router.get("/api/agent-attributes/{attribute_id}", response_model=schemas.AgentAttribute)
def read_agent_attribute(attribute_id: int, db: Session = Depends(get_db)):
    db_agent_attr = db.query(models.AgentAttribute).filter(models.AgentAttribute.attribute_id == attribute_id).first()
    if db_agent_attr is None:
        raise HTTPException(status_code=404, detail="Agent attribute not found")
    return db_agent_attr

@router.get("/api/agent-types/{type_id}/attributes/{attr_def_id}/values", response_model=List[schemas.AgentAttribute])
def read_attribute_values_by_type(
    type_id: int,
    attr_def_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all attribute values for a specific attribute definition across all agents of a specific type.
    """
    # Verify agent type exists
    db_agent_type = db.query(models.AgentType).filter(models.AgentType.type_id == type_id).first()
    if db_agent_type is None:
        raise HTTPException(status_code=404, detail="Agent type not found")
    
    # Verify attribute definition exists and belongs to the specified type
    db_attr_def = db.query(models.AttributeDefinition).filter(
        models.AttributeDefinition.attr_def_id == attr_def_id,
        models.AttributeDefinition.type_id == type_id
    ).first()
    if db_attr_def is None:
        raise HTTPException(status_code=404, detail="Attribute definition not found for this agent type")
    
    # Get all agents of the specified type
    agent_ids = db.query(models.AgentRegistry.agent_id).filter(
        models.AgentRegistry.type_id == type_id
    ).all()
    agent_ids = [agent_id[0] for agent_id in agent_ids]  # Extract agent_ids from result tuples
    
    if not agent_ids:
        return []
    
    # Get all attribute values for the specified attribute definition and agents
    attr_values = db.query(models.AgentAttribute).filter(
        models.AgentAttribute.attr_def_id == attr_def_id,
        models.AgentAttribute.agent_id.in_(agent_ids)
    ).offset(skip).limit(limit).all()
    
    return attr_values

@router.put("/api/agent-attributes/{attribute_id}", response_model=schemas.AgentAttribute)
def update_agent_attribute(
    attribute_id: int, 
    agent_attr: schemas.AgentAttributeUpdate, 
    db: Session = Depends(get_db), 
    auth_agent_id: int = Depends(verify_agent_signature)
):
    # Get the attribute
    db_agent_attr = db.query(models.AgentAttribute).filter(models.AgentAttribute.attribute_id == attribute_id).first()
    if db_agent_attr is None:
        raise HTTPException(status_code=404, detail="Agent attribute not found")
    
    # Verify that the authenticated agent is updating its own attribute
    if auth_agent_id != db_agent_attr.agent_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this attribute")
    
    for key, value in agent_attr.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_agent_attr, key, value)
    
    db_agent_attr.last_updated = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_agent_attr)
    return db_agent_attr

@router.delete("/api/agent-attributes/{attribute_id}", response_model=schemas.AgentAttribute)
def delete_agent_attribute(attribute_id: int, db: Session = Depends(get_db), auth_agent_id: int = Depends(verify_agent_signature)):
    # Get the attribute
    db_agent_attr = db.query(models.AgentAttribute).filter(models.AgentAttribute.attribute_id == attribute_id).first()
    if db_agent_attr is None:
        raise HTTPException(status_code=404, detail="Agent attribute not found")
    
    # Verify that the authenticated agent is deleting its own attribute
    if auth_agent_id != db_agent_attr.agent_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this attribute")
    
    db.delete(db_agent_attr)
    db.commit()
    return db_agent_attr
