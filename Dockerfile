# Use official n8n image as base (already includes Node.js and n8n)
FROM n8nio/n8n:latest

# Switch to root to install additional packages
USER root

# Install system dependencies for Python and FFmpeg
# Keep it minimal - only what's needed for your workflow
RUN apk add --update --no-cache \
    python3 \
    py3-pip \
    ffmpeg \
    ca-certificates

# Install Python libraries with --break-system-packages flag (required for Alpine)
RUN pip3 install --break-system-packages --no-cache-dir \
    edge-tts \
    requests \
    yt-dlp

# Create necessary directories and set permissions
RUN mkdir -p /home/node/output /home/node/temp && \
    chown -R node:node /home/node

# Copy the Python script
COPY --chown=node:node shorts_maker.py /home/node/shorts_maker.py
RUN chmod +x /home/node/shorts_maker.py

# Switch back to node user for security
USER node

# The official n8n image already handles:
# - N8N_USER_FOLDER=/home/node/.n8n
# - EXPOSE 5678
# - Proper entrypoint and CMD
# So we don't need to redefine them
