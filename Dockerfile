# Use Python 3.11 slim image
FROM python:3.11





RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

WORKDIR /app

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* ./

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY --chown=user . /app
CMD ["python", "src/app.py"]
