# Use official n8n image - pure n8n setup for workflow orchestration
FROM n8nio/n8n:latest

# No additional dependencies needed - this is a pure n8n instance
# All UI features (Share, Activate, Save) will be available
# Python processing can be handled via Hugging Face Spaces or other services

# The official n8n image already includes:
# - n8n with all features enabled
# - Node.js runtime
# - All standard n8n nodes
# - Proper entrypoint and configuration
# - Port 5678 exposed

# Just use the base image as-is for maximum compatibility
