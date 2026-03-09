# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy poetry files first for better caching
COPY pyproject.toml poetry.lock /app/

# Install dependencies (no virtualenv in container)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi

# Copy the rest of the application
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["sh", "-c", "sleep 20 && uvicorn app.main:app --host 0.0.0.0 --port 80 --reload"]
