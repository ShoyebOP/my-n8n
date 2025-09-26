# Use a minimal Python image as yt-dlp is a Python application
FROM python:3.11-slim

# Install ffmpeg (often needed by yt-dlp for merging formats) and your API components
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg aria2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install yt-dlp using pip for the latest version
RUN pip install --no-cache-dir yt-dlp pycryptodomex

# =======================================================
# === START: Portable Remote Command API Section ===
COPY ../api-components/apiserver /usr/local/bin/apiserver
COPY ../api-components/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/apiserver /usr/local/bin/entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# === END: Portable Remote Command API Section ===
