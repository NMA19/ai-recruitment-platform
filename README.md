# AI-Powered Recruitment Platform

A modern recruitment platform with an AI chatbot interface for job searching and applications.

## 🏗️ Architecture

The system follows a **Layered Microservice-Oriented Architecture** integrating an AI service for natural language understanding.

```
┌──────────────────────────────┐
│        Frontend (React)      │
│   Chat UI + User Dashboard   │
└───────────────▲──────────────┘
                │ API Requests
┌───────────────┴──────────────┐
│        Backend API            │
│        (FastAPI - Python)     │
└───────────────▲──────────────┘
                │
        Business Logic Layer
                │
 ┌──────────────┴──────────────┐
 │        AI Service Layer       │
 │        (OpenAI Model)         │
 └──────────────▲───────────────┘
                │
┌───────────────┴──────────────┐
│        Database Layer          │
│   Users • Jobs • Applications  │
└───────────────────────────────┘
```

## 📁 Project Structure

```
PFE/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Configuration & security
│   │   ├── db/              # Database connection
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic & AI
│   ├── requirements.txt
│   ├── seed.py              # Sample data
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── components/      # React components
    │   ├── pages/           # Page components
    │   ├── services/        # API calls
    │   └── context/         # Auth context
    ├── package.json
    └── tailwind.config.js
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (or SQLite for testing)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (database URL, OpenAI key)

# Run database migrations (tables auto-create)
# Seed sample data
python seed.py

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔑 Demo Accounts

After running `seed.py`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | admin123 |
| Recruiter | recruiter@example.com | recruiter123 |
| Candidate | john@example.com | john123 |
| Candidate | alice@example.com | alice123 |

## 🤖 AI Features

The chatbot understands natural language queries:

- **"Find me Python jobs in Algiers"** → Searches jobs by skill and location
- **"Show me internships"** → Filters by contract type
- **"Apply for job #5"** → Submits application
- **"Show my applications"** → Lists user's applications

## 📚 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login (get JWT token)
- `GET /auth/me` - Get current user

### Chat (AI)
- `POST /chat` - Send message (authenticated)
- `POST /chat/guest` - Send message (guest)
- `GET /chat/history` - Get chat history

### Jobs
- `GET /jobs` - List all jobs
- `GET /jobs/{id}` - Get job details
- `POST /jobs` - Create job (recruiter)
- `PUT /jobs/{id}` - Update job
- `DELETE /jobs/{id}` - Delete job

### Applications
- `POST /apply` - Apply for job
- `GET /apply` - My applications
- `PUT /apply/{id}/status` - Update status (recruiter)

## 🔧 Configuration

### Environment Variables (backend/.env)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/recruitment_db
SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=sk-your-openai-api-key  # Optional
```

### Using SQLite (for testing)

Change `DATABASE_URL` in `.env`:
```env
DATABASE_URL=sqlite:///./recruitment.db
```

## 📝 For Your PFE Report

### Architecture Type
> The system follows a **Layered Microservice-Oriented Architecture** integrating an AI service for natural language understanding.

### Key Features
1. **Separation of Concerns** - Each layer has specific responsibilities
2. **AI Integration** - Natural language processing for job search
3. **Scalable Design** - Modular components
4. **Modern Web Stack** - FastAPI, React, Tailwind CSS

### Technologies Used
- **Frontend**: React.js, Tailwind CSS, Vite
- **Backend**: FastAPI, Python, SQLAlchemy
- **Database**: PostgreSQL
- **AI**: OpenAI API (GPT-3.5/4)
- **Authentication**: JWT tokens

## 📄 License

MIT License - Free for academic use
