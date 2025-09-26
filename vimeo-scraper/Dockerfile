# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install Chromium and its driver for Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
COPY ./vimeo-scraper/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python scraper script into the container
COPY ./vimeo-scraper/find_vimeo_url.py .

# =======================================================
# === START: Portable Remote Command API Section ===
COPY ../api-components/apiserver /usr/local/bin/apiserver
COPY ../api-components/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/apiserver /usr/local/bin/entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# === END: Portable Remote Command API Section ===

