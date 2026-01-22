# Start from a known Alpine-based n8n image
# Use a specific version tag that's known to be Alpine-based
FROM n8nio/n8n:1.17.1-alpine

# Switch to root user to install software
USER root

# Install system dependencies for Alpine Linux
# python3: Python runtime
# py3-pip: Python package manager
# ffmpeg: Video processing engine
# git: For potential future extensions
# bash: Shell for better script compatibility
RUN apk add --update --no-cache \
    python3 \
    py3-pip \
    ffmpeg \
    git \
    bash

# Install Python libraries with --break-system-packages flag (required for Alpine)
# edge-tts: AI voice generation
# requests: HTTP client for Pexels API  
# yt-dlp: Video downloader (backup method)
RUN pip3 install --break-system-packages --no-cache-dir \
    edge-tts \
    requests \
    yt-dlp

# Create output and temp directories with proper permissions
RUN mkdir -p /home/node/output /home/node/temp && \
    chown -R node:node /home/node/output /home/node/temp

# Copy the Python script into the image
COPY shorts_maker.py /home/node/shorts_maker.py

# Set proper permissions for the script
RUN chmod +x /home/node/shorts_maker.py && \
    chown node:node /home/node/shorts_maker.py

# Switch back to node user for security
USER node

# Set working directory
WORKDIR /home/node
