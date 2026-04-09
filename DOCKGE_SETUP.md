# Quick start guide for Dockge integration

## One-Time Setup

### 1. Start with Dockge included:
```bash
docker compose -f docker-compose.dockge.yml up -d
```

### 2. Access Dockge:
Open http://localhost:5001 in your browser.

### 3. Login:
Default username: `admin`
Default password: `admin`
(Change these immediately in Dockge settings!)

### 4. Add your stack to Dockge:
In Dockge UI:
- Click **"Stacks"** 
- Click **"Create Stack"**
- Choose **"From Compose File"**
- Copy-paste the contents of `docker-compose.dockge.yml`
- Click **"Deploy"**

Now your stack is visible in Dockge and fully editable via the UI.

---

## Managing via Dockge UI

### View Stack Status:
- Dashboard shows all containers (postgres, backend, frontend, dockge)
- Green = healthy, Yellow = restarting, Red = stopped

### Edit & Redeploy:
- Click the stack name
- Edit environment variables, ports, volumes directly in the UI
- Click "Deploy" to apply changes (recreates affected containers)

### View Logs:
- Click any container → **"Logs"** tab
- Real-time streaming or download logs

### Restart Services:
- Click container → **"Restart"** button
- No downtime for other services

---

## CLI Fallback (if needed):

For pure CLI management without Dockge, use:
```bash
docker compose -f compose.yaml up -d
docker compose -f compose.yaml logs -f backend
docker compose -f compose.yaml restart backend
```

---

## Important Notes

1. **Two compose files:**
   - `compose.yaml` — CLI-based deployment (no Dockge)
   - `docker-compose.dockge.yml` — Includes Dockge UI for web management

2. **Use one or the other, not both simultaneously** — they would create duplicate stacks.

3. **Secrets in Dockge:**
   - Dockge stores stack definitions in `/app/data` (Docker volume)
   - Always use environment variables (`.env`) for secrets, never hardcode in compose

4. **Production Deployments:**
   - For production, skip Dockge and use `compose.yaml` with a CI/CD pipeline
   - Dockge is best for development/staging environments

---

## Troubleshooting

### Dockge won't start:
```bash
docker logs dockge
```

### Can't access http://localhost:5001:
- Check if Dockge container is running: `docker ps | grep dockge`
- Verify port 5001 isn't already in use: `netstat -tlnp | grep 5001`

### Stack not appearing in Dockge:
- Refresh the page (hard refresh: Ctrl+Shift+R)
- Check Dockge logs for errors
- Verify compose file YAML syntax (use an online validator)

### Changes in Dockge not applying:
- Ensure .env file exists with correct values
- Check container logs for startup errors
- Verify database migrations completed: `docker compose logs backend | grep "Migrations complete"`
