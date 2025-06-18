# Production Deployment Guide

This guide covers deploying Toolbox.io with automated MySQL setup.

## **🚀 Quick Deployment**

### **Single Command Deployment**
```bash
# Build and run
docker build -t toolbox-io . && \
docker run -d \
  --name toolbox-io-prod \
  -p 80:80 \
  -p 443:443 \
  -p 3306:3306 \
  -v toolbox_mysql_data:/root/site/server/data \
  -v caddy_data:/data \
  -v caddy_config:/config \
  --restart unless-stopped \
  toolbox-io
```

### **With Persistent Data**
```bash
# Create volumes
docker volume create toolbox_mysql_data
docker volume create caddy_data
docker volume create caddy_config

# Deploy
docker run -d \
  --name toolbox-io-prod \
  -p 80:80 \
  -p 443:443 \
  -p 3306:3306 \
  -v toolbox_mysql_data:/root/site/server/data \
  -v caddy_data:/data \
  -v caddy_config:/config \
  --restart unless-stopped \
  toolbox-io
```

## **🔧 What Happens Automatically**

The Dockerfile and main.py handle everything:

1. **MySQL Setup (main.py)**
   - Creates data directory at `/root/site/server/data`
   - Sets proper permissions
   - Initializes MySQL if data directory is empty
   - Starts MySQL server
   - Waits for MySQL to be ready
   - Creates database `toolbox_db` and user `toolbox_user`
   - Creates database tables
   - Creates test user if needed

2. **Application Setup (main.py)**
   - Starts FastAPI application
   - Starts Caddy reverse proxy

3. **Services**
   - **MySQL**: Port 3306 (accessible from host)
   - **FastAPI**: Port 8000 (internal)
   - **Caddy**: Ports 80/443 (HTTP/HTTPS)

## **📋 Connection Details**

| Service | Host | Port | Details |
|---------|------|------|---------|
| **Web App** | localhost | 80/443 | Main application |
| **Database** | localhost | 3306 | MySQL for IntelliJ IDEA |
| **API** | localhost | 8000 | FastAPI (internal) |

**Database Credentials:**
- **Database**: `toolbox_db`
- **Username**: `toolbox_user`
- **Password**: `toolbox_password`
- **Connection String**: `mysql+pymysql://toolbox_user:toolbox_password@localhost:3306/toolbox_db`

## **🔍 Monitoring & Management**

### **View Logs**
```bash
docker logs -f toolbox-io-prod
```

### **Access Container**
```bash
docker exec -it toolbox-io-prod bash
```

### **Connect to MySQL**
```bash
docker exec -it toolbox-io-prod mysql -u toolbox_user -p toolbox_db
```

### **Backup Database**
```bash
docker exec toolbox-io-prod mysqldump -u toolbox_user -ptoolbox_password toolbox_db > backup.sql
```

### **Restore Database**
```bash
docker exec -i toolbox-io-prod mysql -u toolbox_user -ptoolbox_password toolbox_db < backup.sql
```

## **🛠️ Troubleshooting**

### **Container Won't Start**
```bash
# Check logs
docker logs toolbox-io-prod

# Check if ports are in use
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :3306
```

### **MySQL Connection Issues**
```bash
# Check MySQL status
docker exec toolbox-io-prod mysqladmin ping -h localhost

# Check MySQL logs
docker exec toolbox-io-prod tail -f /var/log/mysql/error.log
```

### **Reset Everything**
```bash
# Stop and remove container
docker stop toolbox-io-prod
docker rm toolbox-io-prod

# Remove volumes (WARNING: This deletes all data!)
docker volume rm toolbox_mysql_data caddy_data caddy_config

# Recreate and redeploy
docker volume create toolbox_mysql_data
docker volume create caddy_data
docker volume create caddy_config
docker run -d --name toolbox-io-prod -p 80:80 -p 443:443 -p 3306:3306 -v toolbox_mysql_data:/root/site/server/data -v caddy_data:/data -v caddy_config:/config --restart unless-stopped toolbox-io
```

## **🔒 Security Notes**

- Default passwords are for development only
- Change `toolbox_password` for production
- Consider using environment variables for sensitive data
- Enable SSL for production database connections
- Regularly backup your data volume

## **📊 Performance**

The setup includes:
- **MySQL**: Optimized InnoDB settings
- **FastAPI**: Async Python framework
- **Caddy**: Modern reverse proxy with automatic HTTPS
- **Data Persistence**: Docker volumes for data survival

## **🔄 Updates**

To update the application:
```bash
# Stop container
docker stop toolbox-io-prod

# Remove container (data stays in volumes)
docker rm toolbox-io-prod

# Rebuild and redeploy
docker build -t toolbox-io .
docker run -d --name toolbox-io-prod -p 80:80 -p 443:443 -p 3306:3306 -v toolbox_mysql_data:/root/site/server/data -v caddy_data:/data -v caddy_config:/config --restart unless-stopped toolbox-io
```

## **🧪 Local Development**

For local development without Docker:

```bash
# Start MySQL
brew services start mysql

# Create database and user
mysql -u root -e "CREATE DATABASE IF NOT EXISTS toolbox_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER IF NOT EXISTS 'toolbox_user'@'localhost' IDENTIFIED BY 'toolbox_password'; GRANT ALL PRIVILEGES ON toolbox_db.* TO 'toolbox_user'@'localhost'; FLUSH PRIVILEGES;"

# Run the application
cd server
source .venv/bin/activate
python main.py
```

The application will automatically:
- Wait for MySQL to be ready
- Create database tables
- Create test user
- Start the FastAPI server 