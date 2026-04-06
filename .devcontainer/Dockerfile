FROM docker.n8n.io/n8nio/n8n:latest

# Switch to root to install bash (required for Codespace features)
USER root
RUN apk add --no-cache bash git
# Switch back to the default node user
USER node
