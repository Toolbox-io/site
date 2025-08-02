# Multi-Branch Deployment Setup

This setup provides completely isolated environments for running your main and dev branches simultaneously.

## Architecture

### Main Branch (Production)
- **Domain**: `toolbox-io.ru`
- **Download Domain**: `download.toolbox-io.ru`
- **Port**: 8000 (app), 8001 (download), 3306 (database)
- **Database**: `toolbox_db_main`
- **Network**: `toolbox-io-main-network`
- **Volumes**: `toolbox-io-main-data`, `toolbox-io-main-photos`, `toolbox-io-main-download-cache`

### Dev Branch (Development)
- **Domain**: `beta.toolbox-io.ru`
- **Download Domain**: `download-beta.toolbox-io.ru`
- **Port**: 8002 (app), 8003 (download), 3307 (database)
- **Database**: `toolbox_db_dev`
- **Network**: `toolbox-io-dev-network`
- **Volumes**: `toolbox-io-dev-data`, `toolbox-io-dev-photos`, `toolbox-io-dev-download-cache`

## Files

- `docker-compose.main.yml` - Main branch services (isolated)
- `docker-compose.dev.yml` - Dev branch services (isolated)
- `deploy-multi.sh` - Deployment script
- `caddy/Caddyfile` - Updated routing configuration

## Usage

### Deploy Both Environments
```bash
./deploy-multi.sh both
```

### Deploy Only Main
```bash
./deploy-multi.sh main
```

### Deploy Only Dev
```bash
./deploy-multi.sh dev
```

### Rebuild and Deploy
```bash
./deploy-multi.sh both --build
```

### Restart Services
```bash
./deploy-multi.sh both --restart
```

### Check Status
```bash
./deploy-multi.sh status
```

### Stop All Services
```bash
./deploy-multi.sh stop
```

## Environment Variables

Both environments use the same environment variables, but you can override specific ones for dev:

- `DEV_SECRET_KEY` - Secret key for dev environment (defaults to `SECRET_KEY`)
- `DB_PASSWORD` - Database password (shared)
- `SECRET_KEY` - Main secret key
- `SMTP_PASSWORD` - SMTP password
- `GITHUB_APP_ID` - GitHub app ID
- `GITHUB_INSTALLATION_ID` - GitHub installation ID

## Benefits

1. **Complete Isolation**: Each branch has its own database, network, and volumes
2. **Independent Scaling**: Can scale main and dev independently
3. **Safe Testing**: Dev changes don't affect production data
4. **Easy Rollback**: Can stop/start environments independently
5. **Resource Management**: Can allocate different resources to each environment

## Port Mapping

| Service | Main Port | Dev Port | External Port |
|---------|-----------|----------|---------------|
| App | 8000 | 8000 | 8000/8002 |
| Download | 8001 | 8001 | 8001/8003 |
| Database | 3306 | 3306 | 3306/3307 |

## Networks

- `toolbox-io-main-network` - Isolated network for main services
- `toolbox-io-dev-network` - Isolated network for dev services

## Volumes

### Main Environment
- `toolbox-io-main-data` - Main database data
- `toolbox-io-main-photos` - Main photo uploads
- `toolbox-io-main-download-cache` - Main download cache

### Dev Environment
- `toolbox-io-dev-data` - Dev database data
- `toolbox-io-dev-photos` - Dev photo uploads
- `toolbox-io-dev-download-cache` - Dev download cache

## Monitoring

### Check Service Status
```bash
docker compose -f docker-compose.main.yml ps
docker compose -f docker-compose.dev.yml ps
```

### View Logs
```bash
docker compose -f docker-compose.main.yml logs -f
docker compose -f docker-compose.dev.yml logs -f
```

### Resource Usage
```bash
docker stats $(docker compose -f docker-compose.main.yml ps -q)
docker stats $(docker compose -f docker-compose.dev.yml ps -q)
```

## Troubleshooting

### Port Conflicts
If you get port conflicts, check that no other services are using:
- Ports 8000, 8001, 8002, 8003, 3306, 3307

### Database Issues
Each environment has its own database. If you need to reset:
```bash
docker compose -f docker-compose.main.yml down -v
docker compose -f docker-compose.dev.yml down -v
```

### Network Issues
If networks conflict, remove and recreate:
```bash
docker network rm toolbox-io-main-network toolbox-io-dev-network
```

## Migration from Single Environment

If you're migrating from the single environment setup:

1. Stop the old services:
   ```bash
   docker compose down
   ```

2. Deploy the new multi-branch setup:
   ```bash
   ./deploy-multi.sh both --build
   ```

3. Verify both environments are running:
   ```bash
   ./deploy-multi.sh status
   ```

## Security Considerations

- Each environment has its own database with separate credentials
- Networks are isolated to prevent cross-environment communication
- Volumes are separate to prevent data leakage
- Caddy handles SSL termination and security headers for both environments 