# Start with the official n8n image
FROM n8nio/n8n:latest

# Switch to root user to install software
USER root

# Install Python3, pip, and FFmpeg (The "Video Engine" tools)
# Update package list and install dependencies for Debian-based image
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install the Python libraries we need (Edge-TTS and Requests)
RUN pip3 install --no-cache-dir edge-tts requests

# Copy your python script directly into the image
# (Upload shorts_maker.py to your GitHub repo first!)
COPY shorts_maker.py /home/node/shorts_maker.py

# Give permissions to the node user
RUN chown node:node /home/node/shorts_maker.py

# Switch back to the standard n8n user for security
USER node
