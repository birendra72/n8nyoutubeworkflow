# Use latest stable Alpine as base (lightweight, low memory)
FROM alpine:3.19

# Set environment variables for n8n
ENV N8N_VERSION=latest \
    NODE_ENV=production \
    N8N_USER_FOLDER=/home/node/.n8n \
    GENERIC_TIMEZONE=UTC

# Install system dependencies
# - nodejs and npm: For running n8n
# - python3, py3-pip: For our automation script
# - ffmpeg: For video processing
# - git, bash: For compatibility
# - tini: For proper signal handling
RUN apk add --update --no-cache \
    nodejs \
    npm \
    python3 \
    py3-pip \
    ffmpeg \
    git \
    bash \
    tini \
    ca-certificates

# Create node user and directories
RUN addgroup -g 1000 node && \
    adduser -u 1000 -G node -s /bin/sh -D node && \
    mkdir -p /home/node/.n8n /home/node/output /home/node/temp && \
    chown -R node:node /home/node

# Install n8n globally (as root, before switching users)
RUN npm install -g n8n

# Install Python libraries with --break-system-packages flag (required for Alpine)
RUN pip3 install --break-system-packages --no-cache-dir \
    edge-tts \
    requests \
    yt-dlp

# Install Python libraries with --break-system-packages flag (required for Alpine)
RUN pip3 install --break-system-packages --no-cache-dir \
    edge-tts \
    requests \
    yt-dlp

# Copy the Python script
COPY --chown=node:node shorts_maker.py /home/node/shorts_maker.py
RUN chmod +x /home/node/shorts_maker.py

# Switch back to node user
USER node

# Expose n8n port
EXPOSE 5678

# Use tini as entrypoint for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start n8n
CMD ["n8n"]
