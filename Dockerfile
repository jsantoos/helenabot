# syntax=docker/dockerfile:1

FROM python:3.12.7-slim

# Set environment variables
ENV PYTHONPATH=/app:/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app/src

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev \
    ffmpeg libgl1-mesa-glx git curl unzip sudo && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy dependency management files first (to leverage Docker cache)
COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 5001

# Default command
CMD ["python", "-m", "helena_bot.core.startup"]
