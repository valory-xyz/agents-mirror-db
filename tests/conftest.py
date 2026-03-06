import datetime

import pytest
from eth_account import Account as EthAccount
from eth_account.messages import encode_defunct
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.endpoints import router
from app.db import get_db
from app.dependencies import get_api_key, verify_agent_signature
from app.models.models import (
    Agent,
    AgentRegistry,
    AgentType,
    APIKey,
    AttributeDefinition,
    Base,
    Tweet,
    TwitterAccount,
)

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _make_app():
    app = FastAPI()
    app.include_router(router)
    return app


def make_client(db, auth_agent_id=1):
    """Create a TestClient with all auth dependencies overridden."""
    app = _make_app()

    def _get_db():
        yield db

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_api_key] = lambda: "test-key"
    app.dependency_overrides[verify_agent_signature] = lambda: auth_agent_id

    return TestClient(app)


def make_raw_client(db):
    """Create a TestClient with only get_db overridden (real auth)."""
    app = _make_app()

    def _get_db():
        yield db

    app.dependency_overrides[get_db] = _get_db

    return TestClient(app)


# ── Core fixtures ──


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    return make_client(db)


@pytest.fixture
def raw_client(db):
    """Return TestClient with real auth (no overrides except DB)."""
    return make_raw_client(db)


# ── Seed-data fixtures ──


@pytest.fixture
def agent(db):
    a = Agent(agent_name="test-agent")
    db.add(a)
    db.commit()
    db.refresh(a)
    key = APIKey(key="seed-api-key", agent_id=a.agent_id)
    db.add(key)
    db.commit()
    return a


@pytest.fixture
def twitter_account(db, agent):
    acct = TwitterAccount(
        twitter_user_id="tw_001",
        agent_id=agent.agent_id,
        username="testuser",
        name="Test User",
    )
    db.add(acct)
    db.commit()
    db.refresh(acct)
    return acct


@pytest.fixture
def tweet(db, twitter_account):
    t = Tweet(
        tweet_id=100001,
        twitter_user_id=twitter_account.twitter_user_id,
        user_name="testuser",
        text="hello world",
        created_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@pytest.fixture
def agent_type(db):
    at = AgentType(type_name="TestBot", description="A test bot type")
    db.add(at)
    db.commit()
    db.refresh(at)
    return at


@pytest.fixture
def attr_def(db, agent_type):
    ad = AttributeDefinition(
        type_id=agent_type.type_id,
        attr_name="personality",
        data_type="string",
        is_required=True,
    )
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


@pytest.fixture
def registry(db, agent_type):
    r = AgentRegistry(
        agent_name="reg-agent",
        type_id=agent_type.type_id,
        eth_address="0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@pytest.fixture
def eth_account():
    """Return a fresh Ethereum account for signature tests."""
    return EthAccount.create()


def sign_message(account, message):
    """Sign a message with an eth_account and return hex signature."""
    signable = encode_defunct(text=message)
    signed = account.sign_message(signable)
    return signed.signature.hex()
