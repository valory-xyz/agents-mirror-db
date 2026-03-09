import datetime

from app.models.models import (
    Agent,
    Interaction,
    InteractionType,
    Tweet,
    TwitterAccount,
)


class TestCreateTwitterAccount:
    def test_success(self, client, agent):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/twitter_accounts/",
            json={
                "twitter_user_id": "tw_new",
                "username": "newuser",
                "name": "New User",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["twitter_user_id"] == "tw_new"
        assert "created_at" in data

    def test_duplicate_twitter_user_id(self, client, agent, twitter_account):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/twitter_accounts/",
            json={
                "twitter_user_id": twitter_account.twitter_user_id,
                "username": "other",
                "name": "Other",
            },
        )
        assert resp.status_code == 409


class TestGetTwitterAccount:
    def test_success(self, client, twitter_account):
        resp = client.get(f"/api/twitter_accounts/{twitter_account.twitter_user_id}")
        assert resp.status_code == 200
        assert resp.json()["username"] == "testuser"

    def test_not_found(self, client):
        resp = client.get("/api/twitter_accounts/nonexistent")
        assert resp.status_code == 404


class TestGetTwitterAccountsByAgent:
    def test_success(self, client, twitter_account, agent):
        resp = client.get(f"/api/agents/{agent.agent_id}/twitter_accounts/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_no_accounts(self, client, agent):
        resp = client.get(f"/api/agents/{agent.agent_id}/twitter_accounts/")
        assert resp.status_code == 404


class TestActiveUsernames:
    def test_one_per_agent(self, client, db):
        """Each agent should return only their most recent username."""
        a1 = Agent(agent_name="agent1")
        a2 = Agent(agent_name="agent2")
        db.add_all([a1, a2])
        db.commit()
        db.refresh(a1)
        db.refresh(a2)

        # Agent 1 has two accounts — most recent first (ordered by created_at desc)
        acct1_old = TwitterAccount(
            twitter_user_id="a1_old",
            agent_id=a1.agent_id,
            username="a1_old_name",
            name="Old",
            created_at=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
        )
        acct1_new = TwitterAccount(
            twitter_user_id="a1_new",
            agent_id=a1.agent_id,
            username="a1_new_name",
            name="New",
            created_at=datetime.datetime(2024, 6, 1, tzinfo=datetime.timezone.utc),
        )
        acct2 = TwitterAccount(
            twitter_user_id="a2_only",
            agent_id=a2.agent_id,
            username="a2_name",
            name="Agent2",
            created_at=datetime.datetime(2024, 3, 1, tzinfo=datetime.timezone.utc),
        )
        db.add_all([acct1_old, acct1_new, acct2])
        db.commit()

        resp = client.get("/api/active_usernames/")
        assert resp.status_code == 200
        usernames = resp.json()
        assert len(usernames) == 2
        # Most recent account per agent
        assert "a1_new_name" in usernames
        assert "a2_name" in usernames

    def test_no_accounts(self, client):
        resp = client.get("/api/active_usernames/")
        assert resp.status_code == 404


class TestActiveTwitterAccounts:
    def test_filters_by_recent_activity(self, client, db):
        """Only accounts with tweets or interactions in the last 7 days."""
        agent1 = Agent(agent_name="active-agent")
        agent2 = Agent(agent_name="inactive-agent")
        db.add_all([agent1, agent2])
        db.commit()
        db.refresh(agent1)
        db.refresh(agent2)

        acct_active = TwitterAccount(
            twitter_user_id="active_tw",
            agent_id=agent1.agent_id,
            username="active",
            name="Active",
        )
        acct_inactive = TwitterAccount(
            twitter_user_id="inactive_tw",
            agent_id=agent2.agent_id,
            username="inactive",
            name="Inactive",
        )
        db.add_all([acct_active, acct_inactive])
        db.commit()

        # Active account has a recent tweet
        recent_tweet = Tweet(
            tweet_id=999,
            twitter_user_id="active_tw",
            user_name="active",
            text="recent",
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        # Inactive account has an old tweet
        old_tweet = Tweet(
            tweet_id=998,
            twitter_user_id="inactive_tw",
            user_name="inactive",
            text="old",
            created_at=datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=30),
        )
        db.add_all([recent_tweet, old_tweet])
        db.commit()

        resp = client.get("/api/active_twitter_accounts/")
        assert resp.status_code == 200
        accounts = resp.json()
        assert len(accounts) == 1
        assert accounts[0]["username"] == "active"

    def test_active_via_interaction(self, client, db):
        """An agent with a recent interaction (but no recent tweets) is active."""
        a = Agent(agent_name="interactor")
        db.add(a)
        db.commit()
        db.refresh(a)

        acct = TwitterAccount(
            twitter_user_id="inter_tw",
            agent_id=a.agent_id,
            username="interactor",
            name="Interactor",
        )
        db.add(acct)
        db.commit()

        # Create a tweet for the interaction FK
        t = Tweet(
            tweet_id=555,
            twitter_user_id=None,
            user_name="someone",
            text="target",
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        db.add(t)
        db.commit()

        interaction = Interaction(
            tweet_id=555,
            agent_id=a.agent_id,
            user_id=None,
            interaction_type=InteractionType.like,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        db.add(interaction)
        db.commit()

        resp = client.get("/api/active_twitter_accounts/")
        assert resp.status_code == 200
        assert resp.json()[0]["username"] == "interactor"

    def test_no_active_accounts(self, client, db):
        """All accounts inactive → 404."""
        a = Agent(agent_name="stale")
        db.add(a)
        db.commit()
        db.refresh(a)

        acct = TwitterAccount(
            twitter_user_id="stale_tw",
            agent_id=a.agent_id,
            username="stale",
            name="Stale",
        )
        db.add(acct)
        db.commit()

        resp = client.get("/api/active_twitter_accounts/")
        assert resp.status_code == 404
