# Agents Fun Mirror DB

This project is a FastAPI-based application for managing agents, Twitter accounts, tweets, and interactions. It uses SQLAlchemy for ORM and Pydantic for data validation.

## Features

- Create and manage agents
- Create and manage Twitter accounts
- Create and manage tweets
- Create and manage interactions (like, retweet, reply, quote tweet, follow)
- API key generation and validation

## Project Structure

```
agents_fun_mirror_db/
├── app/
│   ├── api/
│   │   └── endpoints.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── dependencies.py
│   └── utils.py
├── alembic/
├── tests/
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL 

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/valory-xyz/agents_fun_mirror_db.git
   cd agents_fun_mirror_db
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:

   ```bash
   alembic upgrade head
   ```

5. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

### API Endpoints

- **Create Agent**: `POST /api/agents/`
- **Get Agent**: `GET /api/agents/{agent_id}`
- **Create Twitter Account**: `POST /api/agents/{agent_id}/twitter_accounts/`
- **Get Twitter Account**: `GET /api/twitter_accounts/{twitter_user_id}`
- **Create Tweet**: `POST /api/agents/{agent_id}/accounts/{twitter_user_id}/tweets/`
- **Get Tweet**: `GET /api/tweets/{tweet_id}`
- **Create Interaction**: `POST /api/agents/{agent_id}/accounts/{twitter_user_id}/interactions/`
- **Get Interaction**: `GET /api/interactions/{interaction_id}`
- **Get Interactions by Twitter User ID**: `GET /api/twitter_accounts/{twitter_user_id}/interactions/`

### Example Requests

#### Create Agent

```bash
curl -X POST "http://127.0.0.1:8000/api/agents/" -H "Content-Type: application/json" -d '{"agent_name": "Agent007"}'
```

#### Create Twitter Account

```bash
curl -X POST "http://127.0.0.1:8000/api/agents/1/twitter_accounts/" -H "Content-Type: application/json" -d '{"username": "johndoe", "name": "John Doe", "twitter_user_id": "12345"}'
```

## Running Tests

To run the tests, use the following command:

```bash
pytest
```

## License

This project is licensed under the MIT License.

```

```
