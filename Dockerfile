# Start with the official n8n image
FROM n8nio/n8n:latest

# Switch to root user to install software
USER root

# Install Python3, pip, and FFmpeg (The "Video Engine" tools)
RUN apk add --update --no-cache python3 py3-pip ffmpeg

# Install the Python libraries we need (Edge-TTS and Requests)
# We use --break-system-packages because Alpine manages python differently now, 
# this is safe for a container.
RUN pip3 install edge-tts requests --break-system-packages

# Copy your python script directly into the image
# (Upload shorts_maker.py to your GitHub repo first!)
COPY shorts_maker.py /home/node/shorts_maker.py

# Give permissions to the node user
RUN chown node:node /home/node/shorts_maker.py

# Switch back to the standard n8n user for security
USER node
