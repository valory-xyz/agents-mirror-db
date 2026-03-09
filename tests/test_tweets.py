import datetime

from app.models.models import Agent


class TestCreateTweet:
    def test_success(self, client, agent, twitter_account):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/tweets/",
            json={
                "tweet_id": 200001,
                "user_name": "testuser",
                "text": "my tweet",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["tweet_id"] == 200001
        assert data["text"] == "my tweet"

    def test_missing_tweet_id(self, client, agent, twitter_account):
        resp = client.post(
            f"/api/agents/{agent.agent_id}/accounts/{twitter_account.twitter_user_id}/tweets/",
            json={
                "user_name": "testuser",
                "text": "no id",
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            },
        )
        assert resp.status_code == 400
        assert "tweet_id is required" in resp.json()["detail"]


class TestReadTweet:
    def test_success(self, client, tweet):
        resp = client.get(f"/api/tweets/{tweet.tweet_id}")
        assert resp.status_code == 200
        assert resp.json()["text"] == "hello world"

    def test_not_found(self, client):
        resp = client.get("/api/tweets/9999999")
        assert resp.status_code == 404


class TestGetLatestTweetsByAgent:
    def test_success(self, client, agent, tweet):
        resp = client.get(f"/api/agents/{agent.agent_id}/twitter_accounts/tweets/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_no_twitter_accounts(self, client, db):
        a = Agent(agent_name="lonely")
        db.add(a)
        db.commit()
        db.refresh(a)

        resp = client.get(f"/api/agents/{a.agent_id}/twitter_accounts/tweets/")
        assert resp.status_code == 404
