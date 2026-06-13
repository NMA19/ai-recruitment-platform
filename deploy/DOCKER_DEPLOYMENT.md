# Docker Deployment Guide

This guide covers deploying the Wassit AI Chatbot using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- 2GB+ RAM available
- At least 500MB disk space

## Quick Start

### 1. Clone and Configure

```bash
# Clone or navigate to the project
cd wassit-ai-chatbot

# Create .env file from example
cp .env.example .env

# Edit .env and add your GROQ_API_KEY
nano .env
```

### 2. Build and Start Services

```bash
# Build the images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. Verify Deployment

```bash
# Check backend health
curl http://localhost:5000/health

# Check frontend
curl http://localhost

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost/api
```

## Configuration

### Environment Variables

Edit `.env` file to configure:

| Variable | Description | Default |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq LLM API key (required) | - |
| `FLASK_ENV` | Flask environment | production |
| `PORT` | Backend port | 5000 |
| `WASSIT_DB_PATH` | Database file path | backend/data/wassit.db |
| `CHAT_RATE_LIMIT` | Max requests per minute | 20 |
| `MAX_CONTENT_LENGTH` | Max upload size | 8MB |

### Backend-specific

- **Database**: SQLite file at `/app/data/wassit.db`
- **Logs**: Written to `/app/logs/backend.log`
- **Backups**: Stored in `/app/backups/`
- **Profiles Pictures**: Stored in `/app/data/profile_pictures/`

## Service Management

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last N lines
docker-compose logs --tail=100 backend
```

### Restart Services

```bash
# Single service
docker-compose restart backend

# All services
docker-compose restart

# Force rebuild
docker-compose up -d --build
```

### Stop Services

```bash
# Stop running services
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove volumes too (WARNING: deletes data!)
docker-compose down -v
```

## Backup and Maintenance

### Database Backup

```bash
# Automatic backup using the db-backup service
docker-compose --profile backup run db-backup

# Manual backup
docker exec wassit-backend python backup_db.py
```

Backups are saved to `backend/backups/` with timestamps.

### Database Restore

```bash
# Copy backed-up database
cp backend/backups/wassit_backup_*.db backend/data/wassit.db

# Restart backend
docker-compose restart backend
```

### Clean Up

```bash
# Remove unused Docker resources
docker system prune

# Remove unused volumes
docker volume prune
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing GROQ_API_KEY: Add it to .env
# - Port 5000 already in use: Change PORT in .env
# - Database permissions: Ensure backend/data is writable
```

### Frontend shows blank page

```bash
# Check logs
docker-compose logs frontend

# Clear browser cache
# Check API connectivity: curl http://localhost/api
```

### File upload fails

```bash
# Check file size limit
echo $(($(grep MAX_CONTENT_LENGTH .env | cut -d= -f2) / 1024 / 1024))MB

# Check disk space
df -h

# Check permissions
ls -la backend/data/
```

### Database issues

```bash
# Check database file
ls -lh backend/data/wassit.db

# Verify database integrity
docker exec wassit-backend python -c "
  import sqlite3
  conn = sqlite3.connect('/app/data/wassit.db')
  cursor = conn.cursor()
  cursor.execute('SELECT COUNT(*) FROM users')
  print(f'Users: {cursor.fetchone()[0]}')
  conn.close()
"
```

## Production Considerations

### 1. Use Production Database

For production, consider using PostgreSQL instead of SQLite:

```bash
# Add PostgreSQL to docker-compose.yml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_PASSWORD: your-password
    POSTGRES_DB: wassit
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### 2. Enable SSL/TLS

Add a reverse proxy (nginx, Traefik) with SSL:

```bash
# Using nginx with Let's Encrypt
docker run -d \
  -p 443:443 \
  -p 80:80 \
  -v /etc/letsencrypt:/etc/letsencrypt \
  nginx
```

### 3. Monitor and Logging

```bash
# Set up log rotation (in docker-compose.yml)
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### 4. Resource Limits

```yaml
# In docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 5. Security

- [ ] Set strong PASSWORD_SALT in .env
- [ ] Use secrets for sensitive data
- [ ] Enable firewall rules
- [ ] Regular backups
- [ ] Monitor logs for suspicious activity
- [ ] Keep Docker and dependencies updated

## Advanced Configuration

### Custom Port

```bash
# Change frontend port
# In docker-compose.yml, change frontend ports: ["8080:80"]

# Then access at http://localhost:8080
```

### External Database

```bash
# In .env
WASSIT_DB_PATH=/path/to/external/wassit.db
```

### Reverse Proxy Setup

See `nginx-production.conf` for a production-ready configuration.

## Support and Issues

For issues or questions:

1. Check logs: `docker-compose logs backend`
2. Verify .env configuration
3. Ensure ports are available: `netstat -tuln | grep 5000`
4. Check disk space: `df -h`
5. Review this guide's troubleshooting section

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://react.dev/)
