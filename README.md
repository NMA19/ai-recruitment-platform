# Wassit Online - Chatbot ANEM

Plateforme de recrutement avec chatbot IA pour l'ANEM Algérie.

## Lancer le projet

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
python seed.py
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

**URLs:** Frontend http://localhost:5173 | API http://localhost:8000/docs

## Comptes test

- `john@example.com` / `john123` (candidat)
- `admin@example.com` / `admin123` (admin)

## Stack

- **Frontend:** React + Vite + TailwindCSS
- **Backend:** FastAPI + SQLAlchemy
- **IA:** sklearn (ML) + spaCy (NLP) + Ollama/OpenAI (LLM)

## Architecture

```
┌─────────────────────────────────┐
│   Frontend (React + Vite)       │
│   Pages: Chat, Jobs, Dossier    │
└───────────────┬─────────────────┘
                │ REST API
┌───────────────▼─────────────────┐
│   Backend (FastAPI)             │
│   Routes: auth, chat, jobs      │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│   Services IA                   │
│   ML Classifier → NLP → LLM     │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│   Database (SQLite)             │
│   Users, Jobs, Applications     │
└─────────────────────────────────┘
```

## Structure du projet

```
PFE/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # auth, chat, jobs, documents
│   │   ├── core/            # config, security
│   │   ├── db/              # database
│   │   ├── models/          # User, Job, Application
│   │   ├── schemas/         # Pydantic validation
│   │   └── services/
│   │       ├── ai_service.py        # Orchestration IA
│   │       ├── ml_classifier.py     # Intent classification
│   │       ├── ollama_service.py    # LLM local
│   │       ├── candidate_ranking.py # Classement ML
│   │       └── analytics.py         # Métriques
│   ├── requirements.txt
│   └── seed.py
│
└── frontend/
    └── src/
        ├── components/      # ChatBox, Navbar, JobCard
        ├── pages/           # Chat, Jobs, Login, Dossier
        ├── context/         # Auth, Theme, Language
        └── services/        # API calls
```
