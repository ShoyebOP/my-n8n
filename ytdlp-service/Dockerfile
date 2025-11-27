# Use a minimal Python image as yt-dlp is a Python application
FROM python:3.11-slim

# 1. Install curl and unzip (required to download/install Deno) along with ffmpeg and aria2
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    aria2 \
    curl \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Install Deno (The recommended JS runtime for EJS)
# We download the installer, run it, and move the binary to a global path
RUN curl -fsSL https://deno.land/install.sh | sh \
    && mv /root/.deno/bin/deno /usr/local/bin/deno

# 3. Install yt-dlp with [default] extras
# "yt-dlp[default]" ensures 'yt-dlp-ejs' and other standard dependencies are installed
RUN pip install --no-cache-dir "yt-dlp[default]" pycryptodomex

# =======================================================
# === START: Portable Remote Command API Section ===
COPY ../api-components/apiserver /usr/local/bin/apiserver
COPY ../api-components/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/apiserver /usr/local/bin/entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# === END: Portable Remote Command API Section ===
