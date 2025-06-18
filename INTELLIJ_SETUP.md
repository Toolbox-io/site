# IntelliJ IDEA Database Connection Setup

This guide will help you connect IntelliJ IDEA to the MySQL database running in your Toolbox.io application.

## Prerequisites

1. **IntelliJ IDEA** (Community or Ultimate edition)
2. **Database Tools and SQL plugin** (usually included by default)
3. **MySQL Connector/J** (will be downloaded automatically)

## Connection Setup

### Step 1: Open Database Tool Window

1. Open IntelliJ IDEA
2. Go to **View** → **Tool Windows** → **Database** (or press `Ctrl+Alt+L` / `Cmd+Alt+L`)

### Step 2: Add New Data Source

1. Click the **+** button in the Database tool window
2. Select **MySQL** from the list

### Step 3: Configure Connection

Fill in the following details:

```
Host: localhost (or your server IP)
Port: 3306
Database: toolbox_db
User: toolbox_user
Password: toolbox_password
```

### Step 4: Test Connection

1. Click **Test Connection** to verify the setup
2. If successful, click **OK** to save

## Connection Details

| Field | Value |
|-------|-------|
| **Host** | `localhost` (local) or your server IP |
| **Port** | `3306` |
| **Database** | `toolbox_db` |
| **Username** | `toolbox_user` |
| **Password** | `toolbox_password` |
| **URL** | `jdbc:mysql://localhost:3306/toolbox_db?useSSL=false&serverTimezone=UTC` |

## Troubleshooting

### Connection Refused
- Make sure the application is running: `docker run -p 80:80 -p 443:443 -p 3306:3306 toolbox-io`
- Check if port 3306 is exposed: `docker ps`

### Authentication Failed
- Verify the container is running properly
- Check container logs: `docker logs <container_id>`

### SSL Issues
- Add `?useSSL=false` to the connection URL
- Or enable SSL in MySQL configuration

## Useful Commands

```bash
# Build the image
docker build -t toolbox-io .

# Run the application
docker run -d -p 80:80 -p 443:443 -p 3306:3306 --name toolbox-io toolbox-io

# View logs
docker logs -f toolbox-io

# Connect to MySQL directly
docker exec -it toolbox-io mysql -u toolbox_user -p toolbox_db

# Stop the application
docker stop toolbox-io

# Remove container
docker rm toolbox-io
```

## Database Schema

The main table is `users` with the following structure:

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Security Notes

- The default password is for development only
- Change passwords for production use
- Consider using environment variables for sensitive data
- Enable SSL for production connections 