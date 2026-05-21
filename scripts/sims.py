"""Manual sim script that drives the FastAPI service via its HTTP API.

Not part of CI or service runtime. Run locally against a dev server to
populate the DB with synthetic agents, Twitter accounts, tweets, and
interactions for ad-hoc testing.
"""

import datetime
import random
from typing import Any, Dict, List, Optional

import requests

# API base URL
BASE_URL = "http://localhost:8000/api"


def create_agent(agent_name: str) -> Optional[Dict[str, Any]]:
    """POST /agents/ and return the JSON body, or None on failure."""
    url = f"{BASE_URL}/agents/"
    payload = {"agent_name": agent_name}
    response = requests.post(url, json=payload, timeout=30)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating agent: {response.status_code} - {response.text}")
        return None


def create_twitter_account(
    agent_id: int,
    username: str,
    name: str,
    twitter_user_id: str,
    api_key: str,
) -> Optional[Dict[str, Any]]:
    """POST /agents/<id>/twitter_accounts/ and return the JSON body, or None on failure."""
    url = f"{BASE_URL}/agents/{agent_id}/twitter_accounts/"
    headers = {"access-token": api_key}
    payload = {"username": username, "name": name, "twitter_user_id": twitter_user_id}
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Error creating Twitter account: {response.status_code} - {response.text}"
        )
        return None


def create_tweet(
    agent_id: int,
    twitter_user_id: str,
    user_name: str,
    text: str,
    created_at: str,
    api_key: str,
) -> Optional[Dict[str, Any]]:
    """POST /agents/<id>/accounts/<uid>/tweets/ with a random tweet_id, or None on failure."""
    url = f"{BASE_URL}/agents/{agent_id}/accounts/{twitter_user_id}/tweets/"
    headers = {"access-token": api_key}
    tweet_id = random.randint(1000000000000000000, 9223372036854775807)  # nosec B311
    payload: Dict[str, Any] = {
        "tweet_id": tweet_id,
        "user_name": user_name,
        "text": text,
        "created_at": created_at,
    }
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating tweet: {response.status_code} - {response.text}")
        return None


def create_interaction(
    agent_id: int,
    twitter_user_id: str,
    interaction_type: str,
    api_key: str,
    tweet_id: Optional[int] = None,
    user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """POST /agents/<id>/accounts/<uid>/interactions/ and return the JSON body, or None on failure."""
    url = f"{BASE_URL}/agents/{agent_id}/accounts/{twitter_user_id}/interactions/"
    headers = {"access-token": api_key}
    payload = {
        "interaction_type": interaction_type,
        "tweet_id": tweet_id,
        "user_id": user_id,
    }
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating interaction: {response.status_code} - {response.text}")
        return None


def simulate_user_behavior() -> None:
    """Drive the four endpoints above with random inputs to populate the dev DB."""
    # 1. Create an agent
    agent = create_agent("Simulated Agent")
    if not agent:
        print("Failed to create agent. Exiting.")
        return

    agent_id = agent["agent_id"]
    api_key = agent["api_key"]
    print(f"Created agent with ID: {agent_id} and API Key: {api_key}")

    # 2. Create Twitter accounts for the agent
    twitter_accounts: List[Dict[str, Any]] = []
    for i in range(random.randint(1, 2)):  # nosec B311
        twitter_user_id = str(random.randint(1000000000, 9999999999))  # nosec B311
        account = create_twitter_account(
            agent_id,
            f"sim_user_{i + 1}",
            f"Sim User {i + 1}",
            twitter_user_id,
            api_key,
        )
        if account:
            twitter_accounts.append(
                {
                    "agent_id": agent_id,
                    "twitter_user_id": twitter_user_id,
                    "user_name": account["name"],
                }
            )

    if not twitter_accounts:
        print("No Twitter accounts created. Exiting.")
        return

    # 3. Create tweets and interactions for each account
    interaction_types = ["like", "retweet", "reply", "quote_tweet", "follow"]
    for account in twitter_accounts:
        tweet_ids = []
        for i in range(random.randint(2, 4)):  # nosec B311
            created_at = datetime.datetime.now().isoformat()
            tweet = create_tweet(
                account["agent_id"],
                account["twitter_user_id"],
                account["user_name"],
                f"This is a simulated tweet {i + 1}",
                created_at,
                api_key,
            )
            if tweet:
                tweet_ids.append(tweet["tweet_id"])

        for _ in range(random.randint(5, 10)):  # nosec B311
            interaction_type = random.choice(interaction_types)  # nosec B311
            if interaction_type == "follow":
                create_interaction(
                    account["agent_id"],
                    account["twitter_user_id"],
                    interaction_type,
                    api_key,
                    user_id=account["twitter_user_id"],
                )
            elif tweet_ids:
                create_interaction(
                    account["agent_id"],
                    account["twitter_user_id"],
                    interaction_type,
                    api_key,
                    tweet_id=random.choice(tweet_ids),  # nosec B311
                )


if __name__ == "__main__":
    simulate_user_behavior()
    print("Simulated user behavior completed.")
