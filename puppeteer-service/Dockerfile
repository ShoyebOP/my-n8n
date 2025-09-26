FROM node:20-slim

# Install the libraries needed for Puppeteer's browser to run
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-lohit-beng-bengali \
    libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libgtk-3-0 libgbm1 libasound2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Install puppeteer itself
RUN npm install puppeteer

COPY ./puppeteer-service/p.js /usr/src/app/p.js

# =======================================================
# === START: Portable Remote Command API Section ===
COPY ../api-components/apiserver /usr/local/bin/apiserver
COPY ../api-components/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/apiserver /usr/local/bin/entrypoint.sh
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
# === END: Portable Remote Command API Section ===
# =======================================================
