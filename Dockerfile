# Use Python 3.11 version of uv image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Add user - this is the user that will run the app
# If you do not set user, the app will run as root (undesirable)
RUN useradd -m -u 1000 user
USER user

# Set the home directory and path
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH        

ENV UVICORN_WS_PROTOCOL=websockets
ENV PYTHONPATH=/app

# Set the working directory
WORKDIR $HOME/app

# Copy the app to the container
COPY --chown=user . $HOME/app

# Install the dependencies
# RUN uv sync --frozen
RUN uv sync

# Expose the port
EXPOSE 7860

# Run the app - updated path to src/app.py
CMD ["uv", "run", "chainlit", "run", "src/app.py", "--host", "0.0.0.0", "--port", "7860"]