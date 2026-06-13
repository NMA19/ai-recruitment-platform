# Wassit AI Chatbot - API Documentation

Complete API reference for the Wassit AI Chatbot backend.

## Base URL

- Development: `http://localhost:5000`
- Production: `https://your-domain.com/api`

## Authentication

Most endpoints require Bearer token authentication.

### Header Format

```
Authorization: Bearer <access_token>
```

---

## Endpoints

### Health & Info

#### GET /health

Check backend health status.

**Response (200 OK)**
```json
{
  "status": "ok",
  "db": {
    "sessions": 42,
    "messages": 1234,
    "users": 15
  },
  "llm": "connected",
  "jobs": 5000,
  "chunks": 10000
}
```

---

### Authentication

#### POST /auth/register

Create a new user account.

**Request**
```json
{
  "fullName": "John Doe",
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (201 Created)**
```json
{
  "id": 1,
  "fullName": "John Doe",
  "email": "john@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Errors**
- `400 Bad Request`: Missing required fields
- `409 Conflict`: Email already registered

---

#### POST /auth/login

Authenticate with existing credentials.

**Request**
```json
{
  "email": "john@example.com",
  "password": "secure_password_123"
}
```

**Response (200 OK)**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**Errors**
- `401 Unauthorized`: Invalid credentials

---

#### GET /auth/me

Get current authenticated user info.

**Headers**
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**
```json
{
  "id": 1,
  "fullName": "John Doe",
  "email": "john@example.com"
}
```

**Errors**
- `401 Unauthorized`: Missing or invalid token

---

### User Profile

#### GET /auth/profile

Get current user's profile.

**Headers**
```
Authorization: Bearer <access_token>
```

**Response (200 OK)**
```json
{
  "userId": 1,
  "avatarId": "orbit",
  "bio": "Senior Software Engineer",
  "location": "Algiers, Algeria",
  "profession": "Tech Lead",
  "website": "https://example.com",
  "profilePictureUrl": "/profile-pictures/1_abc123.png",
  "preferences": {
    "theme": "dark",
    "language": "ar"
  },
  "updatedAt": "2026-05-29T14:41:52.788035+00:00"
}
```

**Errors**
- `401 Unauthorized`: Missing or invalid token

---

#### PUT /auth/profile

Update current user's profile.

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request**
```json
{
  "avatarId": "avatar-2",
  "bio": "Updated bio",
  "location": "New Location",
  "profession": "New Profession",
  "website": "https://new-site.com",
  "preferences": {
    "theme": "light",
    "language": "en"
  }
}
```

**Response (200 OK)**
```json
{
  "userId": 1,
  "avatarId": "avatar-2",
  "bio": "Updated bio",
  "location": "New Location",
  "profession": "New Profession",
  "website": "https://new-site.com",
  "profilePictureUrl": "/profile-pictures/1_abc123.png",
  "preferences": {
    "theme": "light",
    "language": "en"
  },
  "updatedAt": "2026-05-29T14:41:52.788035+00:00"
}
```

**Errors**
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Missing or invalid token

---

#### POST /auth/profile/picture

Upload a profile picture.

**Headers**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request**
- Form field: `file` (multipart file)
- Accepted formats: PNG, JPG, JPEG, GIF, WebP
- Max size: 5MB

**cURL Example**
```bash
curl -X POST http://localhost:5000/auth/profile/picture \
  -H "Authorization: Bearer <token>" \
  -F "file=@profile.jpg"
```

**Response (200 OK)**
```json
{
  "message": "Profile picture uploaded successfully",
  "profilePictureUrl": "/profile-pictures/1_abc123def456.png"
}
```

**Errors**
- `400 Bad Request`: No file or invalid format
- `401 Unauthorized`: Missing or invalid token
- `413 Payload Too Large`: File exceeds 5MB limit
- `500 Internal Server Error`: Upload failed

---

#### GET /profile-pictures/<filename>

Retrieve a profile picture.

**Response (200 OK)**
- File content (image data)

**Errors**
- `400 Bad Request`: Invalid filename
- `404 Not Found`: File not found

---

### Chat

#### POST /chat

Send a message and get AI response.

**Headers**
```
Content-Type: application/json
```

**Request**
```json
{
  "session_id": "unique_session_identifier",
  "message": "What are the best jobs for software engineers?",
  "cv_text": "Optional CV text for better recommendations",
  "masked": false
}
```

**Response (200 OK)**
```json
{
  "response": "Based on current market trends...",
  "session_id": "unique_session_identifier",
  "jobs": [
    {
      "title": "Senior Developer",
      "company": "Tech Corp",
      "location": "Algiers",
      "skills_match": 95
    }
  ]
}
```

**Errors**
- `400 Bad Request`: Missing required fields
- `429 Too Many Requests`: Rate limit exceeded (20 requests/minute)

**Rate Limiting**
- Limit: 20 requests per minute per IP
- Response includes: `Retry-After` header with seconds to wait

---

#### GET /session/<session_id>

Retrieve chat history for a session.

**Response (200 OK)**
```json
[
  {
    "role": "user",
    "content": "What jobs match my profile?",
    "timestamp": "2026-05-29T14:00:00+00:00"
  },
  {
    "role": "assistant",
    "content": "Based on your profile...",
    "timestamp": "2026-05-29T14:00:05+00:00"
  }
]
```

**Limit**: Returns last 40 messages

---

#### DELETE /session/<session_id>

Delete all messages in a session.

**Response (204 No Content)**
- Empty response on success

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Human-readable error message",
  "code": 400
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 204 | No Content - Success with no body |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Auth required or invalid |
| 409 | Conflict - Resource already exists |
| 413 | Payload Too Large - File too big |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error - Server error |

---

## Request/Response Examples

### Complete Registration and Profile Setup Flow

```bash
# 1. Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Ahmed Ali",
    "email": "ahmed@example.com",
    "password": "secure123"
  }'

# Response
{
  "id": 1,
  "fullName": "Ahmed Ali",
  "email": "ahmed@example.com",
  "access_token": "token123...",
  "token_type": "bearer"
}

# 2. Update profile
curl -X PUT http://localhost:5000/auth/profile \
  -H "Authorization: Bearer token123..." \
  -H "Content-Type: application/json" \
  -d '{
    "avatarId": "avatar-1",
    "bio": "Full-stack developer",
    "location": "Algiers",
    "profession": "Developer"
  }'

# 3. Upload profile picture
curl -X POST http://localhost:5000/auth/profile/picture \
  -H "Authorization: Bearer token123..." \
  -F "file=@photo.jpg"

# 4. Get updated profile
curl -X GET http://localhost:5000/auth/profile \
  -H "Authorization: Bearer token123..."
```

---

## Best Practices

### Authentication
- Store token securely in HTTP-only cookies or secure storage
- Refresh token before expiry (if applicable)
- Don't expose token in logs

### Rate Limiting
- Implement exponential backoff for retries
- Check `Retry-After` header
- Cache responses when possible

### File Uploads
- Validate file type on client side
- Send appropriate Content-Type
- Handle chunked uploads for large files

### Session Management
- Use unique session IDs
- Clean up old sessions periodically
- Store session ID securely on client

### Error Handling
- Check HTTP status code first
- Parse error response for details
- Implement user-friendly error messages

---

## API Versioning

Current API Version: **1.0**

Future breaking changes will use `/api/v2/` endpoint prefix.

---

## Rate Limiting

- **Chat Endpoint**: 20 requests/minute per IP
- **Other Endpoints**: 100 requests/minute per IP
- **Headers**: Includes `RateLimit-Remaining` and `RateLimit-Reset`

---

## CORS Configuration

The API supports Cross-Origin Resource Sharing (CORS) for:
- Development: `http://localhost:3000`
- Production: Configured domain

---

## Webhook Events (Future)

Reserved for future notifications:
- `message.received`
- `user.registered`
- `job.matched`

---

## Support

For API issues or questions:
1. Check this documentation
2. Review error messages carefully
3. Enable debug mode in development
4. Check backend logs: `docker-compose logs backend`

---

## Changelog

### v1.0 (2026-05-29)
- Initial API release
- Authentication endpoints
- Profile management
- Chat functionality
- Profile picture upload
- Rate limiting
- Health check endpoint

---

## Code Examples

### JavaScript/Node.js

```javascript
const API_URL = 'http://localhost:5000';
let token = null;

// Register
async function register(fullName, email, password) {
  const res = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ fullName, email, password })
  });
  const data = await res.json();
  token = data.access_token;
  return data;
}

// Get profile
async function getProfile() {
  const res = await fetch(`${API_URL}/auth/profile`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return res.json();
}

// Send chat message
async function sendMessage(sessionId, message) {
  const res = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message })
  });
  return res.json();
}

// Upload profile picture
async function uploadProfilePicture(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_URL}/auth/profile/picture`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return res.json();
}
```

### Python

```python
import requests

API_URL = 'http://localhost:5000'
token = None

def register(full_name, email, password):
    global token
    res = requests.post(f'{API_URL}/auth/register', json={
        'fullName': full_name,
        'email': email,
        'password': password
    })
    token = res.json()['access_token']
    return res.json()

def get_profile():
    headers = {'Authorization': f'Bearer {token}'}
    return requests.get(f'{API_URL}/auth/profile', headers=headers).json()

def send_message(session_id, message):
    return requests.post(f'{API_URL}/chat', json={
        'session_id': session_id,
        'message': message
    }).json()

def upload_profile_picture(filepath):
    headers = {'Authorization': f'Bearer {token}'}
    with open(filepath, 'rb') as f:
        files = {'file': f}
        return requests.post(
            f'{API_URL}/auth/profile/picture',
            headers=headers,
            files=files
        ).json()
```

---

## Testing

### Using cURL

```bash
# Set variables
TOKEN="your_token_here"
SESSION_ID="test_session_123"

# Test health
curl -X GET http://localhost:5000/health

# Test registration
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"fullName":"Test","email":"test@example.com","password":"pass123"}'

# Test profile
curl -X GET http://localhost:5000/auth/profile \
  -H "Authorization: Bearer $TOKEN"

# Test chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"'$SESSION_ID'","message":"Hello"}'
```

### Using Postman

1. Import the provided Postman collection (if available)
2. Set `base_url` variable to `http://localhost:5000`
3. Set `token` variable after login
4. Run requests from collection

---

Last Updated: 2026-05-29
