import datetime
import random

import requests

# API base URL
BASE_URL = "http://localhost:8000/api"


def create_agent(agent_name):
    url = f"{BASE_URL}/agents/"
    payload = {"agent_name": agent_name}
    response = requests.post(url, json=payload)  # No API key needed for agent creation
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating agent: {response.status_code} - {response.text}")
        return None


def create_twitter_account(agent_id, username, name, twitter_user_id, api_key):
    url = f"{BASE_URL}/agents/{agent_id}/twitter_accounts/"
    headers = {"access-token": api_key}
    payload = {"username": username, "name": name, "twitter_user_id": twitter_user_id}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(
            f"Error creating Twitter account: {response.status_code} - {response.text}"
        )
        return None


def create_tweet(agent_id, twitter_user_id, user_name, text, created_at, api_key):
    url = f"{BASE_URL}/agents/{agent_id}/accounts/{twitter_user_id}/tweets/"
    headers = {"access-token": api_key}
    tweet_id = random.randint(1000000000000000000, 9223372036854775807)
    payload = {
        "tweet_id": tweet_id,
        "user_name": user_name,
        "text": text,
        "created_at": created_at,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating tweet: {response.status_code} - {response.text}")
        return None


def create_interaction(
    agent_id, twitter_user_id, interaction_type, api_key, tweet_id=None, user_id=None
):
    url = f"{BASE_URL}/agents/{agent_id}/accounts/{twitter_user_id}/interactions/"
    headers = {"access-token": api_key}
    payload = {
        "interaction_type": interaction_type,
        "tweet_id": tweet_id,
        "user_id": user_id,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating interaction: {response.status_code} - {response.text}")
        return None


def simulate_user_behavior():
    # 1. Create an agent
    agent = create_agent("Simulated Agent")
    if not agent:
        print("Failed to create agent. Exiting.")
        return

    agent_id = agent["agent_id"]
    api_key = agent["api_key"]
    print(f"Created agent with ID: {agent_id} and API Key: {api_key}")

    # 2. Create Twitter accounts for the agent
    twitter_accounts = []
    for i in range(random.randint(1, 2)):
        twitter_user_id = str(random.randint(1000000000, 9999999999))
        account = create_twitter_account(
            agent_id, f"sim_user_{i+1}", f"Sim User {i+1}", twitter_user_id, api_key
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
        for i in range(random.randint(2, 4)):
            created_at = datetime.datetime.now().isoformat()
            tweet = create_tweet(
                account["agent_id"],
                account["twitter_user_id"],
                account["user_name"],
                f"This is a simulated tweet {i+1}",
                created_at,
                api_key,
            )
            if tweet:
                tweet_ids.append(tweet["tweet_id"])

        for _ in range(random.randint(5, 10)):
            interaction_type = random.choice(interaction_types)
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
                    tweet_id=random.choice(tweet_ids),
                )


if __name__ == "__main__":
    simulate_user_behavior()
    print("Simulated user behavior completed.")
