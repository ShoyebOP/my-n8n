# n8n Docker Setup with Cloudflare Tunnel

Self-hosted [n8n](https://n8n.io/) running in Docker, accessible via [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/). No ports exposed on the host.

## Project Structure

- `compose.yaml` — Docker Compose file with n8n and cloudflared services
- `.env.example` — Template for required environment variables
- `.n8n/` — n8n data directory (database, credentials, workflows) — gitignored
- `local-files/` — Shared volume for file exchange with workflows

## Quick Start

1. **Copy the env template and fill in your values:**
   ```bash
   cp .env.example .env
   ```

2. **Configure `.env`:**
   ```
   N8N_HOST=n8n.yourdomain.com
   CLOUDFLARE_TUNNEL_TOKEN=your-tunnel-token
   GENERIC_TIMEZONE=Asia/Dhaka
   ```

3. **Set up your Cloudflare Tunnel:**
   - Go to [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) > Networks > Tunnels
   - Create a tunnel and copy the token to `.env`
   - Add a public hostname pointing to `http://n8n:5678`

4. **Start the services:**
   ```bash
   docker compose up -d
   ```

5. **Access n8n** at `https://n8n.yourdomain.com/`

## Environment Variables

| Variable | Description |
|----------|-------------|
| `N8N_HOST` | Your n8n domain (configured in Cloudflare tunnel) |
| `CLOUDFLARE_TUNNEL_TOKEN` | Tunnel authentication token |
| `GENERIC_TIMEZONE` | Timezone for workflows (default: `UTC`) |

## Services

- **n8n** — Workflow automation, accessible only via internal Docker network
- **cloudflared** — Cloudflare tunnel connector, only service exposed to the internet

## Node Availability

All built-in nodes are enabled, including:
- Execute Command (shell access)
- SSH
- Read/Write File
- Local File Trigger

Community nodes can be installed from the n8n UI.

## Data Migration (from npm install)

If you had n8n installed via npm, the data in `~/.n8n/` (or `~/n8n-data/.n8n/`) can be directly bind-mounted into the container. The `compose.yaml` mounts `./.n8n` which contains the SQLite database, encryption key, workflows, and credentials.

To migrate:
```bash
cp -r ~/n8n-data/.n8n ./.n8n
docker compose up -d
```

Your encryption key, workflows, and credentials will be preserved.

## Useful Links

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Docker Installation](https://docs.n8n.io/hosting/installation/docker/)
- [Cloudflare Tunnel Setup](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [n8n Environment Variables](https://docs.n8n.io/hosting/configuration/environment-variables/)

## License

MIT
