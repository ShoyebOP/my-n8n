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

## Useful Links

- [n8n Documentation](https://docs.n8n.io/)
- [Cloudflare Tunnel Setup](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [GitHub Codespaces Docs](https://docs.github.com/codespaces)

## License

MIT

---

_This README reflects the project structure and required configuration based on the codebase as of this snapshot. For the latest file tree or code, see the [GitHub repo](https://github.com/ShoyebOP/my-n8n)._
