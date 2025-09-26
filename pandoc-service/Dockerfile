# Use the latest stable Alpine Linux image. It's small and fast.
FROM alpine:latest

# Install the pandoc package from Alpine's repository.
# The 'pandoc-cli' package is the correct one, and we add ca-certificates as a best practice.
RUN apk add --no-cache pandoc-cli ca-certificates

# =======================================================
# === START: Portable Remote Command API Section ===
COPY ../api-components/apiserver /usr/local/bin/apiserver
COPY ../api-components/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/apiserver /usr/local/bin/entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# === END: Portable Remote Command API Section ===
# =======================================================
