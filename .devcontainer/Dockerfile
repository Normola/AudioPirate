# Match Raspberry Pi Zero 2 W environment
# Pi OS is based on Debian Bookworm (as of 2024+)
FROM debian:bookworm-slim

# Install basic packages that come with Pi OS
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    vim \
    nano \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    sudo \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create a 'pi' user to match Pi OS default user
RUN useradd -m -s /bin/bash pi && \
    echo "pi ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /workspace

# Switch to pi user
USER pi
