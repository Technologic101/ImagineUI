# Use Python 3.11 slim image
FROM biggates/poetry:2.0.1-py3.11-slim

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Install Poetry
RUN pip install poetry

WORKDIR /app

# Copy dependency files
COPY --chown=user pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --without-dev --no-interaction --no-ansi

# Copy application code
COPY --chown=user . .

# Set environment variables for HuggingFace Spaces
ENV PYTHONPATH=/app
ENV PORT=7860

# Expose the port Chainlit runs on
EXPOSE 7860

# Command to run the Chainlit app
CMD ["chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "7860"]
