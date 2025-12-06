# my-n8n: Run n8n in GitHub Codespaces

This repository provides a project structure and setup to run [n8n](https://n8n.io/)—a powerful workflow automation tool—inside GitHub Codespaces. It is tailored for extensibility using multiple sidecar services (Pandoc, YoutubeDL, Puppeteer, Vimeo Scraper, Rclone) and cloudflared for secure public access.

## Project Structure

- `compose.yaml` &rarr; Main Docker Compose file orchestrating all services
- `pandoc-service/` &rarr; Pandoc service for document conversion
- `ytdlp-service/` &rarr; YoutubeDL service for downloading videos
- `puppeteer-service/` &rarr; Puppeteer service for HTML/PDF automation
- `vimeo-scraper/` &rarr; Vimeo scraping scripts
- `rclone/` &rarr; Rclone server for file sync
- `local-files/` &rarr; Shared volume for file exchange between services

## Services Included

- **n8n**: The core automation tool
- **cloudflared**: Makes Codespaces accessible with secure tunnels
- **Pandoc, YoutubeDL, Puppeteer, Vimeo Scraper**: Helper services for extra automation
- **Rclone**: Secure file sync via SSH

## Running in GitHub Codespaces

1. **Fork this repo** and open it in a new Codespace.
2. **Set required environment variables.**  
   These must be configured before starting the Codespace to ensure all services work, particularly cloudflared and rclone.  
   Suggested way: Add these variables in your Codespace creation dialog (or in `.env` file).

   **Environment variables to set:**
   ```
   DOMAIN_NAME=<your-domain.com>
   SUBDOMAIN=<your-subdomain>
   GENERIC_TIMEZONE=<e.g. "Asia/Kolkata">
   CLOUDFLARE_TUNNEL_TOKEN=<your-cloudflared-token>
   RCLONE_ROOT_PASSWORD=<custom-root-password>
   ```

   Explanations:
   - `DOMAIN_NAME` & `SUBDOMAIN`: Used to configure n8n’s public URL and webhook endpoints.
   - `GENERIC_TIMEZONE`: Time zone configuration for workflows.
   - `CLOUDFLARE_TUNNEL_TOKEN`: Token for tunnel authentication. ([Cloudflare docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/))
   - `RCLONE_ROOT_PASSWORD`: (for rclone service) Sets the SSH root password for secure access.

3. **Start the services:**  
   Use Docker Compose to start all:
   ```bash
   docker compose up -d
   ```
   All services will launch and connect internally. The n8n UI & webhooks will be exposed via cloudflared.

4. **Access n8n:**  
   Visit `https://<SUBDOMAIN>.<DOMAIN_NAME>/` (or the Codespace-forwarded URL if not using custom domain).

## Customization

- **Add more environment variables** as needed for specific services.
- Each service’s Dockerfile and code can be found in its respective folder.

# Added n8n Codespace Watchdog

[![Download Script](https://img.shields.io/badge/Download-Script-blue?style=for-the-badge&logo=gnu-bash)](YOUR_DOWNLOAD_LINK_HERE)

A smart automation script designed for **Termux (Android)** and **Linux**. It manages your GitHub Codespace running n8n to save costs and automate power management.

### What this script does
1.  **Smart Startup:** Checks if your Codespace is running. If not, it boots it up, waits for Docker to initialize, and starts your containers.
2.  **Activity Monitoring:** Connects to your n8n API every 5 minutes to check for **Running** or **Waiting** workflows.
3.  **Cost Saving:**
    *   **If Busy:** It keeps the Codespace awake (resets the GitHub idle timer).
    *   **If Idle:** It counts down a "Grace Period" (e.g., 15 minutes). If no new work appears, it **automatically shuts down** the Codespace to stop your billing usage.
4.  **SSL Fix:** Includes built-in bypass for Termux SSL certificate issues.

---

### Prerequisites

You need the GitHub CLI (`gh`) and JSON Processor (`jq`) installed.

#### Termux (Android)
```bash
pkg update && pkg upgrade
pkg install gh jq
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install gh jq
```

---

### Setup & Usage

1.  **Authenticate GitHub:**
    Run this command and follow the login steps (select **GitHub.com** and **SSH**):
    ```bash
    gh auth login
    ```

2.  **Get the Script:**
    Download the `n8n_watchdog.sh` file or copy the code.

3.  **Configuration:**
    Open the script (`nano n8n_watchdog.sh`) and edit the top section:
    *   `CS_NAME`: Your Codespace name (found via `gh codespace list`).
    *   `N8N_BASE_URL`: Your n8n link (e.g., `https://n8n.example.com`).
    *   `N8N_API_KEY`: Your key from n8n Settings > Public API.
    *   `PROJECT_PATH`: The path to your folder inside the Codespace.

4.  **Make Executable:**
    ```bash
    chmod +x n8n_watchdog.sh
    ```

5.  **Run:**
    ```bash
    ./n8n_watchdog.sh
    ```

### Controls
*   **Run in Background (Phone):** You can start the script in Termux and switch apps or lock your screen (ensure battery optimization is off for Termux).
*   **Manual Stop:** Press `q` on your keyboard at any time while the script is waiting to immediately stop the Codespace and exit.

## Useful Links

- [n8n Documentation](https://docs.n8n.io/)
- [Cloudflare Tunnel Setup](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [GitHub Codespaces Docs](https://docs.github.com/codespaces)

## License

MIT

---

