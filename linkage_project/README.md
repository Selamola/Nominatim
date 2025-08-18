# Linkage Project

End-to-end record linkage demo with FastAPI backend and Streamlit UI.

## Quick Start

```bash
cp .env.example .env
docker compose up -d --build
```

Open [http://localhost](http://localhost) and log in using the credentials in `.env` (`ADMIN_EMAIL` / `ADMIN_PASSWORD`).

If REDCap is disabled or tokens are missing, a mock dataset is loaded automatically so matching works out of the box.

## Enable REDCap
1. Edit `.env` and set `REDCAP_ENABLED=true` with valid tokens.
2. Restart services:
   ```bash
   docker compose up -d --build
   ```
3. Log in as admin and use **Sync from REDCap** to import records.

## Tests

Run tests inside the API container:

```bash
docker compose exec api pytest -q
```

## HTTPS (production)

Put an HTTPS-terminating reverse proxy or load balancer in front of the provided nginx service. The compose file exposes nginx on port 80 only for local use.
