# Wassit Online - ANEM Recruitment Platform 🇩🇿

AI-powered recruitment platform for ANEM (Agence Nationale de l'Emploi) Algeria with multilingual chatbot (French, Arabic, English).

## Features

- 🤖 **AI Chatbot** - NLP + LLM job search (spaCy + Groq)
- 📁 **Dossier Tracking** - ANEM document management
- 🌍 **Multilingual** - FR/AR/EN with RTL support
- 🌙 **Dark Mode** - Theme toggle
- 🔐 **JWT Auth** - Secure authentication

## Architecture

```
┌──────────────────────────────┐
│     Frontend (React/Vite)    │
│   Chat UI + User Dashboard   │
└───────────────▲──────────────┘
                │ REST API
┌───────────────┴──────────────┐
│     Backend API (FastAPI)    │
└───────────────▲──────────────┘
                │
┌───────────────┴──────────────┐
│       AI Service Layer       │
│   NLP (spaCy) + LLM (Groq)   │
└───────────────▲──────────────┘
                │
┌───────────────┴──────────────┐
│    Database (SQLAlchemy)     │
│  Users • Jobs • Applications │
└──────────────────────────────┘
```

## Project Structure

```
PFE/
├── backend/
│   ├── app/
│   │   ├── api/routes/    # auth, jobs, chat, documents
│   │   ├── core/          # config, security
│   │   ├── db/            # database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # AI service
│   ├── requirements.txt
│   └── seed.py
│
└── frontend/
    ├── src/
    │   ├── components/    # ChatBox, Navbar, JobCard
    │   ├── pages/         # Chat, Jobs, Dossier, Login
    │   ├── context/       # Auth, Theme, Language
    │   └── services/      # API calls
    └── package.json
```

## Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Access
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs

## Environment Variables

```env
# backend/.env
DATABASE_URL=sqlite:///./recruitment.db
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-groq-api-key  # Free at console.groq.com
OPENAI_API_KEY=sk-xxx           # Optional fallback
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Tailwind CSS, Vite |
| Backend | FastAPI, Python |
| Database | SQLAlchemy (SQLite/PostgreSQL) |
| NLP | spaCy, langdetect |
| LLM | Groq (Llama 3.1 - FREE) |

## API Endpoints

| Route | Description |
|-------|-------------|
| `POST /auth/register` | Register user |
| `POST /auth/login` | Login |
| `POST /chat/guest` | Chat (no auth) |
| `GET /jobs` | List jobs |
| `POST /apply` | Apply for job |
| `GET /documents/my-dossier` | Dossier status |

## Demo Accounts

| Email | Password |
|-------|----------|
| admin@example.com | admin123 |
| john@example.com | john123 |

## Chatbot Examples

| Language | Input | Action |
|----------|-------|--------|
| 🇫🇷 French | "Chercher emploi Python à Alger" | Search jobs |
| 🇩🇿 Arabic | "ما هي الوثائق المطلوبة؟" | ANEM FAQ |
| 🇬🇧 English | "Apply for job #5" | Submit application |

## License

MIT
