FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# System deps used by the gateway and local tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama for free/local model hosting inside the container.
# The daemon is started via postCreateCommand / postStartCommand.
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /workspace
