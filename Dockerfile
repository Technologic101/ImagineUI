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

# Switch to non-root user
USER user
WORKDIR /app

# Set up environment variables
ENV PYTHONPATH=/app
ENV PORT=7860

# Configure Poetry
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

# Command to run the Chainlit app
CMD ["poetry", "run", "chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "7860"]
