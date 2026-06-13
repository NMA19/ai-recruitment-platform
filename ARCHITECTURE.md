# Wassit AI Chatbot - System Architecture

Complete system design and architecture of the Wassit AI Chatbot application.

## System Overview 🏗️

Wassit AI is a full-stack intelligent recruitment chatbot that connects job seekers with relevant positions using AI-powered recommendations and natural language understanding.

### Key Components

1. **React Frontend** - Modern UI for chat and profile management
2. **Flask Backend** - RESTful API for business logic
3. **LLM Engine** - Groq-powered AI for recommendations
4. **SQLite Database** - User data and chat history persistence
5. **Docker Infrastructure** - Containerized deployment

## High-Level Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         Client Browser                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │           React + Vite Application                      │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ Pages: Chat, Login, Register                    │  │  │
│  │  │ Components: ChatBox, Profile, Navbar            │  │  │
│  │  │ State: AuthContext, ThemeContext, Language      │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────┘
                 │ HTTP/CORS
                 │ REST API Calls
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ SSL/TLS, Rate Limiting, Compression, Routing           │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────┬─────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐
│   Flask Backend      │  │  Static Assets       │
│  Port: 5000          │  │  (dist/ folder)      │
└──────────┬───────────┘  └──────────────────────┘
           │
    ┌──────┴──────────────────────┐
    │                             │
    ▼                             ▼
┌────────────────────┐     ┌──────────────────┐
│  SQLite Database   │     │ Groq LLM API     │
│  (wassit.db)       │     │ (Remote Service) │
│                    │     │                  │
│ • Users table      │     │ • Recommendations│
│ • Profiles table   │     │ • Conversations  │
│ • Sessions table   │     │ • Job Matching   │
│ • Messages table   │     │                  │
└────────────────────┘     └──────────────────┘
```

## Detailed Component Architecture

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Application                         │
├─────────────────────────────────────────────────────────────┤
│
│  ┌────────────────────────────────────────────────────────┐
│  │               Pages (Route Components)                  │
│  ├────────────────────────────────────────────────────────┤
│  │  • ChatPage          - Main chat interface             │
│  │  • LoginPage         - Authentication form             │
│  │  • RegisterPage      - Account creation form           │
│  └────────────────────────────────────────────────────────┘
│                        ▲
│                        │ Uses
│                        ▼
│  ┌────────────────────────────────────────────────────────┐
│  │             Reusable Components                         │
│  ├────────────────────────────────────────────────────────┤
│  │  • ChatBox           - Message input/display           │
│  │  • MessageBubble     - Individual message              │
│  │  • Navbar            - Top navigation bar              │
│  │  • ProfileModal      - Profile editor                  │
│  │  • JobCard           - Job listing                     │
│  │  • ErrorBoundary     - Error handling                  │
│  └────────────────────────────────────────────────────────┘
│                        ▲
│                        │ Uses
│                        ▼
│  ┌────────────────────────────────────────────────────────┐
│  │         Context (State Management)                     │
│  ├────────────────────────────────────────────────────────┤
│  │  • AuthContext       - User & token state              │
│  │  • ThemeContext      - Light/dark theme                │
│  │  • LanguageContext   - I18n language                   │
│  └────────────────────────────────────────────────────────┘
│                        ▲
│                        │ Consumes
│                        ▼
│  ┌────────────────────────────────────────────────────────┐
│  │         API Service Layer                              │
│  ├────────────────────────────────────────────────────────┤
│  │  • api.js (Axios instance)                             │
│  │    - auth endpoints                                    │
│  │    - profile endpoints                                 │
│  │    - chat endpoints                                    │
│  └────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

### Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                         │
├─────────────────────────────────────────────────────────────┤
│
│  ┌────────────────────────────────────────────────────────┐
│  │               HTTP Request Handler                      │
│  ├────────────────────────────────────────────────────────┤
│  │  • CORS Configuration                                  │
│  │  • Rate Limiting Middleware                            │
│  │  • Error Handling                                      │
│  └────────────────────────────────────────────────────────┘
│                        ▼
│  ┌────────────────────────────────────────────────────────┐
│  │              Route Endpoints                            │
│  ├────────────────────────────────────────────────────────┤
│  │  Authentication:                                       │
│  │    • POST /auth/register      Create account          │
│  │    • POST /auth/login         Authenticate            │
│  │    • GET /auth/me             Current user info       │
│  │                                                        │
│  │  Profile:                                             │
│  │    • GET /auth/profile        Get profile             │
│  │    • PUT /auth/profile        Update profile          │
│  │    • POST /auth/profile/picture Upload photo          │
│  │    • GET /profile-pictures/<id> Serve photo           │
│  │                                                        │
│  │  Chat:                                                │
│  │    • POST /chat               Send message            │
│  │    • GET /session/<id>        Get history             │
│  │    • DELETE /session/<id>     Clear session           │
│  │                                                        │
│  │  System:                                              │
│  │    • GET /health              Health check            │
│  │    • GET /                    API info                │
│  └────────────────────────────────────────────────────────┘
│                        ▼
│  ┌────────────────────────────────────────────────────────┐
│  │          Business Logic & Services                     │
│  ├────────────────────────────────────────────────────────┤
│  │  • Authentication service                              │
│  │  • Profile management                                 │
│  │  • Rate limiting                                      │
│  │  • Chat processing                                    │
│  │  • User token generation                              │
│  └────────────────────────────────────────────────────────┘
│                        ▼
│  ┌────────────────────────────────────────────────────────┐
│  │          Database Layer (database.py)                  │
│  ├────────────────────────────────────────────────────────┤
│  │  • User management                                     │
│  │  • Profile operations                                 │
│  │  • Message persistence                                │
│  │  • Session management                                 │
│  └────────────────────────────────────────────────────────┘
│                        ▼
│  ┌────────────────────────────────────────────────────────┐
│  │         External Services                              │
│  ├────────────────────────────────────────────────────────┤
│  │  • Groq LLM API      - AI recommendations              │
│  │  • File Storage      - Profile pictures                │
│  │  • SQLite Database   - Data persistence                │
│  └────────────────────────────────────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### User Registration Flow

```
┌──────────────────┐
│   User Submits   │
│  Registration    │
│   Form (React)   │
└────────┬─────────┘
         │ POST /auth/register
         │ {fullName, email, password}
         ▼
┌──────────────────────────────────┐
│   Backend Validates Input        │
│   • Check required fields        │
│   • Validate email format        │
│   • Check password length        │
└────────┬─────────────────────────┘
         │ Success
         ▼
┌──────────────────────────────────┐
│   Hash Password with Salt        │
│   password_hash = SHA256(salt + │
│   password)                      │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│   Create User Record in DB       │
│   INSERT INTO users (...)        │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│   Create Default Profile        │
│   INSERT INTO user_profiles     │
│   with avatar_id='orbit'        │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│   Generate Auth Token           │
│   token = token_urlsafe(32)     │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│   Return Response to Frontend    │
│   {access_token, user_info}     │
└────────┬─────────────────────────┘
         │ Store token (secure storage)
         ▼
┌──────────────────┐
│  User Logged In  │
│   Navigate to    │
│   Chat Page      │
└──────────────────┘
```

### Chat Message Flow

```
┌──────────────────────────┐
│  User Types Message      │
│  "What jobs match me?"   │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Check Rate Limit                │
│  (20 messages/minute per IP)     │
└────────┬─────────────────────────┘
         │ Pass
         ▼
┌──────────────────────────────────┐
│  POST /chat                      │
│  {session_id, message,           │
│   cv_text, masked}               │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Build LLM Message Context       │
│  • System prompt                 │
│  • Last 20 messages              │
│  • Current user message          │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Call Groq LLM API               │
│  stream=true for streaming       │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Process LLM Response            │
│  • Extract text                  │
│  • Parse job recommendations     │
│  • Extract metadata              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Save Messages to Database       │
│  • User message                  │
│  • Assistant response            │
│  • Session metadata              │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Return Response to Frontend     │
│  {response, jobs, timestamp}     │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Display in Chat UI      │
│  • Show AI response      │
│  • List job cards        │
│  • Update session        │
└──────────────────────────┘
```

### Profile Update Flow

```
┌────────────────────────────────────┐
│  User Edits Profile in Modal       │
│  (bio, location, profession, etc)  │
└────────┬─────────────────────────────┘
         │ Upload Picture (Optional)
         ▼
┌────────────────────────────────────┐
│  POST /auth/profile/picture        │
│  multipart/form-data: {file}       │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Backend Validates File            │
│  • Check file type                 │
│  • Check file size < 5MB           │
│  • Allowed: PNG, JPG, GIF, WebP   │
└────────┬─────────────────────────────┘
         │ Valid
         ▼
┌────────────────────────────────────┐
│  Generate Unique Filename          │
│  filename = user_id + UUID + ext   │
│  e.g., "1_abc123def456.png"        │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Save File to Disk                 │
│  /app/data/profile_pictures/       │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Update Database                   │
│  UPDATE user_profiles              │
│  SET profile_picture_path = ...    │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  PUT /auth/profile                 │
│  {avatarId, bio, location,         │
│   profession, website,             │
│   preferences}                     │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Validate Input                    │
│  • Check authentication            │
│  • Check for empty fields          │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Update in Database                │
│  UPDATE user_profiles              │
│  WHERE user_id = current_user      │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Retrieve Updated Profile          │
│  SELECT * FROM user_profiles ...   │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│  Return Profile to Frontend        │
│  {userId, avatarId, bio,           │
│   profilePictureUrl, ...}          │
└────────┬─────────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  Update UI with        │
│  New Profile Data      │
│  Show Picture Preview  │
└────────────────────────┘
```

## Database Schema

### Entity-Relationship Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ USERS (Core User Account)                                    │
├──────────────────────────────────────────────────────────────┤
│ ┌─ PK  id: INTEGER                                           │
│ │      full_name: TEXT (NOT NULL)                            │
│ │      email: TEXT (NOT NULL, UNIQUE)                        │
│ │      password_hash: TEXT (NOT NULL)                        │
│ │      created_at: TEXT (NOT NULL)                           │
│ └─ IndexByEmail                                              │
└──────────────────────────────────────────────────────────────┘
        │
        │ 1:1
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ USER_PROFILES (Extended Profile Info)                        │
├──────────────────────────────────────────────────────────────┤
│ ┌─ FK  user_id: INTEGER → users.id (PRIMARY KEY)            │
│ │      avatar_id: TEXT (DEFAULT 'orbit')                     │
│ │      bio: TEXT                                             │
│ │      location: TEXT                                        │
│ │      profession: TEXT                                      │
│ │      website: TEXT                                         │
│ │      profile_picture_path: TEXT                            │
│ │      preferences_json: TEXT (JSON)                         │
│ │      updated_at: TEXT (NOT NULL)                           │
│ └                                                            │
└──────────────────────────────────────────────────────────────┘

        │
        │ 1:M
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ AUTH_TOKENS (Session Tokens)                                 │
├──────────────────────────────────────────────────────────────┤
│ ┌─ PK  token: TEXT (PRIMARY KEY)                             │
│ │ ├─ FK  user_id: INTEGER → users.id                         │
│ │      created_at: TEXT (NOT NULL)                           │
│ └                                                            │
└──────────────────────────────────────────────────────────────┘

        ┌─────────────┬──────────────────────────────┐
        │             │                              │
        │ 1:M         │ 1:M                          │
        │             │                              │
        ▼             ▼                              ▼
┌──────────┐  ┌────────────────────┐  ┌──────────────────────┐
│ SESSIONS │  │ CHAT_SESSIONS      │  │ CHAT_MESSAGES        │
├──────────┤  ├────────────────────┤  ├──────────────────────┤
│ PK: ID   │  │ PK: session_id     │  │ PK: id               │
│ ...      │  │ created_at         │  │ FK: session_id       │
│          │  │ updated_at         │  │ role (user/assistant)│
│          │  │                    │  │ content (TEXT)       │
│          │  │                    │  │ payload_json         │
│          │  │                    │  │ created_at           │
│          │  │                    │  │ Index: session_id    │
│          │  │                    │  │ Index: created_at    │
└──────────┘  └────────────────────┘  └──────────────────────┘
```

## Technology Stack 🛠️

### Frontend
- **React 18** - UI library with hooks
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS
- **Context API** - State management
- **Playwright** - E2E testing

### Backend
- **Python 3.11** - Programming language
- **Flask** - Web framework
- **SQLite3** - Database
- **python-dotenv** - Environment config
- **werkzeug** - WSGI utilities
- **requests** - HTTP library
- **PIL/Pillow** - Image processing

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy, web server
- **Let's Encrypt** - SSL certificates

### External Services
- **Groq LLM API** - AI/ML models

## Security Architecture 🔒

### Authentication Flow

```
User Credentials
      ▼
 SHA256(salt + password)  ────► Hash stored in DB
      ▲
      │ Verification
      │ SHA256(salt + provided_pass)
      │ Compare with stored hash
      │
     if match ───► Generate token ───► token_urlsafe(32)
                         │
                         ▼
                  Store in DB: auth_tokens
                         │
                         ▼
                  Return to Frontend
                         │
                         ▼
                  Frontend: Bearer token in headers
                         │
                         ▼
                  Backend: Extract from "Authorization" header
                         │
                         ▼
                  Lookup in auth_tokens table
                         │
                         ▼
                  Get associated user
```

### Rate Limiting

```
Request arrives
      │
      ▼
Extract IP + Endpoint
      │
      ▼
Token Bucket Algorithm
      │
      ├─ Capacity: 20 tokens/minute
      │
      ├─ Refill rate: 2 tokens/second
      │
      ├─ Check available tokens
      │
      ├─ if tokens available:
      │    Remove 1 token
      │    Allow request ──► 200 OK
      │
      └─ if no tokens:
           Return 429 Too Many Requests
           Include Retry-After header
```

### Data Protection

- **Passwords**: Salted SHA256 hashing
- **Tokens**: URL-safe 32-character random strings
- **File Uploads**: Type and size validation
- **CORS**: Frontend domain whitelisting
- **SQL Injection**: Parameterized queries
- **XSS**: React automatic escaping
- **HTTPS/SSL**: Production encryption

## Deployment Architecture

### Docker Compose Stack

```
┌─────────────────────────────────────────────────────────┐
│         Docker Compose Orchestration                    │
├─────────────────────────────────────────────────────────┤
│
│  ┌──────────────────────────────────────────────────┐
│  │ Backend Service (Flask)                          │
│  │ • Image: backend:latest                          │
│  │ • Port: 5000:5000                                │
│  │ • Volumes:                                       │
│  │   - ./backend/data → /app/data                   │
│  │   - ./backend/logs → /app/logs                   │
│  │   - ./backend/backups → /app/backups             │
│  │ • Environment: GROQ_API_KEY, etc.                │
│  │ • Health Check: /health endpoint                 │
│  └──────────────────────────────────────────────────┘
│                    │
│  ┌──────────────────────────────────────────────────┐
│  │ Frontend Service (Nginx + React)                 │
│  │ • Image: frontend:latest                         │
│  │ • Port: 80:80                                    │
│  │ • Proxy: /api → backend:5000                     │
│  │ • Static: /dist → React build                    │
│  │ • Depends on: backend (healthy)                  │
│  └──────────────────────────────────────────────────┘
│
│  ┌──────────────────────────────────────────────────┐
│  │ DB Backup Service (Optional)                     │
│  │ • Profile: backup                                │
│  │ • Command: python backup_db.py                   │
│  │ • Runs on demand                                 │
│  └──────────────────────────────────────────────────┘
│
│  wassit-network (bridge network)
│  All services connected for internal communication
│
└─────────────────────────────────────────────────────────┘
```

## Performance Considerations 📊

### Frontend Optimization
- Code splitting by routes
- Lazy component loading
- Asset minification
- Gzip compression
- Browser caching headers
- Image optimization

### Backend Optimization
- Database indexes on foreign keys
- Connection pooling (SQLite)
- Rate limiting for resource protection
- Message pagination (last 40)
- Session expiration

### Database Optimization
- Index on `session_id, created_at` for fast queries
- Proper foreign key relationships
- DELETE ON CASCADE for cleanup
- Regular backups

## Scalability Path 📈

### Current Capacity (SQLite)
- ~10,000 users
- ~100,000 messages
- Suitable for small/medium deployments

### Future Scaling (Phase 2)
1. **PostgreSQL** - Replace SQLite for better concurrency
2. **Redis** - Add caching layer
3. **Celery** - Background job processing
4. **Kubernetes** - Container orchestration
5. **Load Balancer** - Multiple backend instances
6. **CDN** - Static asset distribution

## Error Handling & Logging 📋

### Backend Error Handling

```
Request → Validation → Business Logic → Response
   ↓         ↓             ↓              ↓
  400     Validate input  Exception    Error response
  401     Check auth       Try/Catch    Log error
  429     Rate limit       Handle       Return HTTP code
  500     Server error     Fallback     User-friendly msg
```

### Logging Strategy

- **INFO**: All requests and important events
- **DEBUG**: Detailed execution flow (dev only)
- **WARNING**: Potentially problematic situations
- **ERROR**: Exceptions and failures
- **Rotation**: 1MB per file, 3 backup files

## Testing Strategy 🧪

### Frontend Testing
- **Unit**: React components with Jest
- **E2E**: Playwright for user workflows
- **Visual**: Manual review of UI

### Backend Testing
- **Unit**: Python unittest/pytest
- **Integration**: API endpoint testing
- **Load**: Rate limiting verification

## Deployment Pipeline

```
Code Push
   │
   ▼
GitHub Actions / CI
   │
   ├─ Lint & Format
   ├─ Unit Tests
   ├─ Build Docker images
   │
   ▼
Docker Registry
   │
   ├─ backend:latest
   ├─ frontend:latest
   │
   ▼
Docker Compose (Staging)
   │
   ├─ Deploy
   ├─ Run tests
   ├─ Health check
   │
   ▼
Manual Approval
   │
   ▼
Docker Compose (Production)
   │
   ├─ Deploy with blue-green
   ├─ Monitor
   ├─ Rollback if needed
   │
   ▼
Live Application
```

## Conclusion

Wassit AI Chatbot is architected as a modern, scalable full-stack application with:

- **Clear separation of concerns** between frontend and backend
- **Secure authentication** with token-based sessions
- **Efficient data storage** with proper indexing
- **Rate limiting** to prevent abuse
- **Production-ready** deployment with Docker
- **Extensible design** for future features

The architecture supports current needs while providing a path for scaling to larger user bases and more complex features.

---

**Last Updated**: 2026-05-29  
**Architecture Version**: 1.0
