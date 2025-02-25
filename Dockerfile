# Use Python 3.11 slim image
FROM biggates/poetry:2.0.1-py3.11-slim

# Run system updates and installations as root
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory with correct permissions
RUN mkdir /app && chown -R 1000:1000 /app

# Create non-root user
RUN useradd -m -u 1000 user

# Set up Poetry environment as root
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# Switch to non-root user
USER user
WORKDIR /app

# Set up Python path and Poetry config
ENV PATH="/home/user/.local/bin:$PATH"
ENV PYTHONPATH=/app
ENV PORT=7860
ENV VIRTUAL_ENV=/home/user/.venv

# Configure Poetry to use virtualenvs
RUN poetry config virtualenvs.create true \
    && poetry config virtualenvs.in-project true

# Copy dependency files with correct ownership
COPY --chown=user pyproject.toml poetry.lock* ./

# Install dependencies in virtualenv
RUN poetry install --no-root --no-interaction --no-ansi

# Copy application code
COPY --chown=user . .

# Expose the port Chainlit runs on
EXPOSE 7860

# Command to run the Chainlit app using Poetry
CMD ["poetry", "run", "chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "7860"]
