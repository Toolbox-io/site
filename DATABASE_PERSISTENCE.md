# Database Persistence for Toolbox.io

## Overview

The Toolbox.io authentication system uses SQLite for user data storage. This document explains how database persistence is configured and managed.

## Database Location

- **Container Path**: `/root/site/server/data/users.db`
- **Host Path**: `./data/users.db` (when using docker-compose)
- **Systemd Service**: `/root/site/data/users.db`

## Persistence Methods

### 1. Docker Compose (Recommended)

The easiest way to ensure database persistence is using docker-compose:

```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down

# View logs
docker-compose logs -f
```

**Benefits:**
- Automatic volume mounting
- Easy environment variable management
- Built-in health checks
- Simple backup and restore

### 2. Systemd Service

The systemd service automatically mounts a volume for persistence:

```bash
# Start the service
sudo systemctl start server

# Check status
sudo systemctl status server

# View logs
sudo journalctl -u server -f
```

**Volume Mount:**
- Host: `/root/site/data`
- Container: `/root/site/server/data`

### 3. Manual Docker Run

For manual deployment:

```bash
# Create data directory
mkdir -p ./data

# Run container with volume mount
docker run -d \
  --name toolbox-io \
  -p 80:80 \
  -p 443:443 \
  -v $(pwd)/data:/root/site/server/data \
  site
```

## Database Backup

### Automatic Backup Script

Use the provided backup script:

```bash
# Create backup
./scripts/db-backup.sh

# List backups
ls -la backups/
```

**Features:**
- Timestamped backups
- Automatic cleanup (keeps last 10 backups)
- Size reporting
- Error handling

### Manual Backup

```bash
# Stop the application
docker-compose down

# Copy database
cp data/users.db backups/users_$(date +%Y%m%d_%H%M%S).db

# Restart application
docker-compose up -d
```

## Database Restore

### From Backup

```bash
# Stop the application
docker-compose down

# Restore from backup
cp backups/users_YYYYMMDD_HHMMSS.db data/users.db

# Restart application
docker-compose up -d
```

### Database Reset

To reset the database (removes all users):

```bash
# Stop the application
docker-compose down

# Remove database
rm data/users.db

# Restart application (will create new database with test user)
docker-compose up -d
```

## Database Schema

The database contains a single table:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Monitoring

### Check Database Size

```bash
# Check database file size
ls -lh data/users.db

# Check database contents (requires sqlite3)
sqlite3 data/users.db "SELECT COUNT(*) as user_count FROM users;"
```

### View Database Contents

```bash
# List all users
sqlite3 data/users.db "SELECT id, username, email, created_at FROM users;"

# Check specific user
sqlite3 data/users.db "SELECT * FROM users WHERE username='testuser';"
```

## Troubleshooting

### Database Not Persisting

1. **Check volume mount:**
   ```bash
   docker inspect toolbox-io | grep -A 10 "Mounts"
   ```

2. **Verify data directory:**
   ```bash
   ls -la data/
   ```

3. **Check permissions:**
   ```bash
   ls -la data/users.db
   ```

### Database Corruption

1. **Stop the application**
2. **Restore from backup**
3. **Check logs for errors**

### Performance Issues

For high-traffic applications, consider:

1. **Regular backups**
2. **Database optimization**
3. **Monitoring disk space**

## Security Considerations

1. **Backup encryption** for sensitive data
2. **Secure backup storage**
3. **Regular security audits**
4. **Access control** for database files

## Environment Variables

- `SECRET_KEY`: JWT secret key (set in docker-compose.yml or environment)
- Database path is configured in `server/database.py`

## Migration

When updating the application:

1. **Backup current database**
2. **Update application**
3. **Test with backup data**
4. **Deploy to production**

## Support

For database issues:

1. Check application logs
2. Verify volume mounts
3. Test backup/restore procedures
4. Review this documentation 