from app.models.models import Tweet


class TestCreateInteraction:
    def test_follow_requires_user_id(self, client, agent, twitter_account):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "follow", "user_id": "target_user"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["interaction_type"] == "follow"
        assert data["user_id"] == "target_user"

    def test_follow_missing_user_id(self, client, agent, twitter_account):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "follow"},
        )
        assert resp.status_code == 400
        assert "user_id is required" in resp.json()["detail"]

    def test_like_requires_tweet_id(self, client, agent, twitter_account, tweet):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "like", "tweet_id": tweet.tweet_id},
        )
        assert resp.status_code == 200
        assert resp.json()["interaction_type"] == "like"

    def test_like_missing_tweet_id(self, client, agent, twitter_account):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "like"},
        )
        assert resp.status_code == 400
        assert "tweet_id is required" in resp.json()["detail"]

    def test_auto_creates_tweet_if_missing(self, client, agent, twitter_account, db):
        """When tweet_id references a non-existent tweet, one is auto-created."""
        unknown_tweet_id = 999888
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "retweet", "tweet_id": unknown_tweet_id},
        )
        assert resp.status_code == 200

        # Verify the tweet was auto-created
        auto_tweet = db.query(Tweet).filter(Tweet.tweet_id == unknown_tweet_id).first()
        assert auto_tweet is not None
        assert auto_tweet.user_name == "unknown"
        assert auto_tweet.text == ""
        assert auto_tweet.twitter_user_id is None

    def test_retweet(self, client, agent, twitter_account, tweet):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "retweet", "tweet_id": tweet.tweet_id},
        )
        assert resp.status_code == 200
        assert resp.json()["interaction_type"] == "retweet"

    def test_reply(self, client, agent, twitter_account, tweet):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "reply", "tweet_id": tweet.tweet_id},
        )
        assert resp.status_code == 200
        assert resp.json()["interaction_type"] == "reply"

    def test_quote_tweet(self, client, agent, twitter_account, tweet):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "quote_tweet", "tweet_id": tweet.tweet_id},
        )
        assert resp.status_code == 200
        assert resp.json()["interaction_type"] == "quote_tweet"


class TestGetInteraction:
    def test_success(self, client, agent, twitter_account, tweet):
        # Create an interaction first
        create_resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "like", "tweet_id": tweet.tweet_id},
        )
        iid = create_resp.json()["interaction_id"]

        resp = client.get(f"/api/interactions/{iid}")
        assert resp.status_code == 200
        assert resp.json()["interaction_id"] == iid

    def test_not_found(self, client):
        resp = client.get("/api/interactions/9999")
        assert resp.status_code == 404


class TestGetInteractionsByAgent:
    def test_success(self, client, agent, twitter_account, tweet):
        client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "like", "tweet_id": tweet.tweet_id},
        )
        resp = client.get(f"/api/agents/{agent.agent_id}/interactions/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_no_interactions(self, client, agent):
        resp = client.get(f"/api/agents/{agent.agent_id}/interactions/")
        assert resp.status_code == 404


class TestGetInteractionsByTwitterUser:
    def test_success(self, client, agent, twitter_account, tweet):
        client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/interactions/",
            json={"interaction_type": "like", "tweet_id": tweet.tweet_id},
        )
        resp = client.get(
            f"/api/twitter_accounts/{twitter_account.twitter_user_id}/interactions/"
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_no_interactions(self, client, twitter_account):
        resp = client.get(
            f"/api/twitter_accounts/{twitter_account.twitter_user_id}/interactions/"
        )
        assert resp.status_code == 404
