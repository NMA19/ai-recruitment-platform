# Backend API Server

The Flask-based REST API backend for Wassit AI Chatbot.

## Overview

This backend provides:
- RESTful API for authentication and user management
- Chat interface with Groq LLM integration
- SQLite database with automatic backups
- Profile management with file uploads
- Rate limiting and error handling
- Production-ready logging

## Quick Start

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Edit .env and add GROQ_API_KEY
```

### Run

```bash
# Development
python app.py
# Server runs on http://localhost:5000

# Debug mode
FLASK_DEBUG=1 python app.py

# With custom port
PORT=8000 python app.py
```

## Configuration 🔧

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | ✅ Yes | - | API key for Groq LLM |
| `FLASK_ENV` | No | `production` | Flask environment |
| `FLASK_DEBUG` | No | `0` | Debug mode (0 or 1) |
| `PORT` | No | `5000` | Server port |
| `PASSWORD_SALT` | No | `wassit-salt` | Password hashing salt |
| `WASSIT_DB_PATH` | No | `backend/data/wassit.db` | Database file path |
| `CHAT_RATE_LIMIT` | No | `20` | Requests per minute |
| `MAX_CONTENT_LENGTH` | No | `8388608` | Max upload size (bytes) |

### Creating .env

```bash
# Copy example
cp ../.env.example .env

# Edit with your values
nano .env
```

Example .env:
```env
GROQ_API_KEY=your_key_here
FLASK_ENV=production
PORT=5000
WASSIT_DB_PATH=backend/data/wassit.db
CHAT_RATE_LIMIT=20
MAX_CONTENT_LENGTH=8388608
```

## Project Structure

```
backend/
├── app.py                 # Main Flask application
├── database.py            # Database models & functions
├── backup_db.py          # Database backup utility
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── data/                # Data directory
│   ├── wassit.db       # SQLite database
│   └── profile_pictures/ # User profile photos
├── logs/                # Application logs
│   └── backend.log
├── backups/             # Database backups
└── README.md            # This file
```

## API Endpoints 📡

### Core Routes

**Authentication**
- `POST /auth/register` - Create account
- `POST /auth/login` - Login
- `GET /auth/me` - Current user info
- `GET /auth/profile` - User profile
- `PUT /auth/profile` - Update profile
- `POST /auth/profile/picture` - Upload picture

**Chat**
- `POST /chat` - Send message
- `GET /session/<id>` - Chat history
- `DELETE /session/<id>` - Clear session

**System**
- `GET /` - API info
- `GET /health` - Health status

### Example Requests

```bash
# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "User",
    "email": "user@example.com",
    "password": "pass123"
  }'

# Chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session123",
    "message": "Hello!"
  }'
```

See [API Documentation](../API_DOCUMENTATION.md) for complete reference.

## Database 🗄️

### Overview

The app stores chat sessions and messages in `backend/data/wassit.db` by default.
Set `WASSIT_DB_PATH` to override the database location.

### Schema

**Users Table**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

**User Profiles**
```sql
CREATE TABLE user_profiles (
    user_id INTEGER PRIMARY KEY,
    avatar_id TEXT DEFAULT 'orbit',
    bio TEXT,
    location TEXT,
    profession TEXT,
    website TEXT,
    profile_picture_path TEXT,
    preferences_json TEXT,
    updated_at TEXT NOT NULL
);
```

**Chat Sessions & Messages**
```sql
CREATE TABLE chat_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    payload_json TEXT,
    created_at TEXT NOT NULL
);
```

### Backups

Create a timestamped copy of the SQLite database:

```bash
python backup_db.py
```

The backup is written to `backend/backups/` and is ignored by git.

### Database Operations

```bash
# Initialize database
python -c "from database import init_db; init_db()"

# Backup database
python backup_db.py

# Database stats
sqlite3 data/wassit.db "SELECT COUNT(*) FROM users;"

# Query messages
sqlite3 data/wassit.db "SELECT * FROM chat_messages LIMIT 5;"
```

## Logging 📋

### Overview

Backend logs are written to `backend/logs/backend.log` and rotated automatically.
Watch them while testing so you can catch failures quickly:

```bash
tail -f logs/backend.log
```

### Log Levels

- **INFO**: General information and requests
- **DEBUG**: Detailed debugging info
- **WARNING**: Potential issues
- **ERROR**: Errors and exceptions

### Accessing Logs

```bash
# Real-time
tail -f logs/backend.log

# Search for errors
grep ERROR logs/backend.log

# Search for session
grep "session_id" logs/backend.log

# Last 100 lines
tail -n 100 logs/backend.log
```

### Log Format

```
2026-05-29 15:34:10,099 [INFO] werkzeug: POST /auth/register HTTP/1.1" 201
```

## Development 🛠️

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# With coverage
pytest --cov=.
```

### Code Structure

```python
# app.py - Main Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# database.py - Database functions
def get_user_by_email(email):
    """Get user by email"""
    pass

def save_message(session_id, role, content):
    """Save chat message"""
    pass

# Models integration
import requai_deploy.app as model_app
```

### Adding New Endpoints

```python
@app.route("/api/new_endpoint", methods=["GET", "POST"])
def new_endpoint():
    # Get authenticated user
    user = current_user_from_request()
    if not user:
        return jsonify({"detail": "Not authenticated"}), 401
    
    # Your logic here
    return jsonify({"result": "success"}), 200
```

## Performance 📊

### Benchmarks
- Response time: < 200ms average
- Concurrent users: 100+ (with rate limiting)
- Database size: ~50MB for 10k users

### Optimization Tips

1. **Enable compression**: Gzip responses
2. **Cache responses**: Use Redis
3. **Database indexes**: Added on session_id, created_at
4. **Connection pooling**: SQLite connection reuse
5. **Rate limiting**: Default 20 req/min

## Deployment 🚀

### Docker

```bash
# Build
docker build -t wassit-backend .

# Run
docker run -p 5000:5000 \
  -e GROQ_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  wassit-backend

# With docker-compose
docker-compose up -d backend
```

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Set `FLASK_DEBUG=0`
- [ ] Strong `PASSWORD_SALT`
- [ ] GROQ_API_KEY configured
- [ ] Database backups scheduled
- [ ] Log rotation enabled
- [ ] Health check configured
- [ ] CORS properly configured

See [Deployment Guide](../deploy/DOCKER_DEPLOYMENT.md) for details.

## Troubleshooting 🐛

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000

# Use different port
PORT=8000 python app.py
```

### GROQ_API_KEY Not Found

```bash
# Check if set
echo $GROQ_API_KEY

# Set it
export GROQ_API_KEY=your_key_here

# Check .env file
cat ../.env
```

### Database Locked

```bash
# SQLite database is locked
# Stop all processes accessing database
ps aux | grep "python app.py"

# Remove lock file (if exists)
rm backend/data/wassit.db-journal

# Restart backend
python app.py
```

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

## Dependencies 📦

Key packages:
- **Flask** - Web framework
- **flask-cors** - CORS handling
- **SQLite3** - Database
- **Werkzeug** - WSGI utilities
- **python-dotenv** - Environment variables

See `requirements.txt` for complete list.

## Security 🔒

### Authentication
- JWT-like tokens with `token_urlsafe(32)`
- Password hashing with SHA256 + salt
- Token stored in auth_tokens table

### Input Validation
- Email format validation
- Password length check (min 6 chars)
- File type validation
- File size limits (5MB max)

### Rate Limiting
- Token bucket algorithm
- 20 requests per minute per IP
- Configurable via CHAT_RATE_LIMIT

### Best Practices
- Use HTTPS in production
- Strong PASSWORD_SALT
- Regular backups
- Monitor logs
- Update dependencies

## Admin Tasks 🔑

### Create Test User

```bash
python -c "
from database import create_user, init_db
init_db()
user_id = create_user('Test User', 'test@example.com', 'pass123')
print(f'Created user {user_id}')
"
```

### Clear Old Sessions

```bash
python -c "
from database import db_session
with db_session() as conn:
    conn.execute('DELETE FROM chat_sessions WHERE datetime(created_at) < datetime(\"now\", \"-7 days\")')
"
```

### View Stats

```bash
python -c "
from database import stats
print(stats())
"
```

## Integration with Frontend

The frontend communicates via HTTP:

```javascript
// Frontend example (React)
const response = await fetch('http://localhost:5000/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    session_id: 'user_session',
    message: 'Hello!'
  })
});
```

See [Frontend README](../frontend/README.md) for details.

## Model assets

The ML artifacts stay in `requai_deploy/` and are loaded by the backend at runtime.

## Support & Issues 💬

- [Main README](../README.md) - Project overview
- [API Documentation](../API_DOCUMENTATION.md) - Complete API reference
- [Architecture](../ARCHITECTURE.md) - System design

---

**Backend Version**: 3.0  
**Last Updated**: 2026-05-29

