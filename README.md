# Wassit Online - ANEM Recruitment Platform 🇩🇿

A modern AI-powered recruitment platform for **ANEM (Agence Nationale de l'Emploi)** - Algeria's National Employment Agency. Features a multilingual chatbot interface (French, Arabic, English) for job searching, applications, and registration dossier tracking.

## ✨ Key Features

- 🤖 **AI Chatbot** - Natural language job search in French, Arabic & English
- 📁 **Dossier Tracking** - Track ANEM registration documents
- 🌍 **Multilingual** - Full FR/AR/EN support with RTL for Arabic
- 🌙 **Dark Mode** - Modern UI with theme toggle
- 📱 **Responsive** - Works on desktop and mobile
- 🔐 **Secure** - JWT authentication

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
│   │   ├── api/routes/      # API endpoints (auth, jobs, chat, documents)
│   │   ├── core/            # Configuration & security
│   │   ├── db/              # Database connection
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic & AI service
│   ├── requirements.txt
│   ├── seed.py              # Sample data
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── components/      # Reusable UI components
    │   ├── pages/           # Page components
    │   ├── services/        # API calls
    │   └── context/         # Auth, Theme, Language contexts
    ├── package.json
    └── tailwind.config.js
```

## 📱 Pages & Features

### 1. Chat Page (`/`)
**The main AI chatbot interface**

| Feature | Description |
|---------|-------------|
| 🔍 Job Search | "Find Python jobs in Algiers" / "Cherche emploi informatique" |
| 📝 Quick Apply | "Apply for job #5" / "Postuler pour l'emploi #5" |
| 🏛️ ANEM FAQ | "How to register?" / "Comment s'inscrire?" |
| 💼 Interview Tips | "Conseils pour l'entretien" / "نصائح للمقابلة" |
| 📊 Sector Filter | "Jobs in healthcare" / "Emplois dans la santé" |
| 🌐 Auto Language | Detects FR/AR/EN and responds accordingly |

### 2. Jobs Page (`/jobs`)
**Browse and filter job listings**

| Feature | Description |
|---------|-------------|
| 📋 Job Cards | Display title, company, location, salary, skills |
| 🔎 Search | Filter by keyword, location, contract type |
| 🏷️ Filters | Full-time, Part-time, Internship, Contract |
| 📍 Wilaya Search | All 58 Algerian wilayas supported |
| ✅ Apply | One-click application for logged-in users |

### 3. Dossier Page (`/dossier`)
**Track ANEM registration documents**

| Feature | Description |
|---------|-------------|
| 📊 Progress Bar | Visual completion percentage |
| 📄 Document List | CNI, Residence, Photos, Diploma, CV, etc. |
| 📤 Upload | Submit documents for review |
| ✅ Status | Not submitted → Pending → Approved/Rejected |
| 📝 Admin Notes | View rejection reasons |
| 🎯 Can Apply | Badge shows when minimum docs approved |

**Required Documents:**
- ✅ Carte Nationale d'Identité (CNI)
- ✅ Certificat de Résidence
- ✅ Photos d'identité
- ✅ Diplômes/Certificats
- ✅ CV (Curriculum Vitae)
- ⚪ Extrait de Naissance (optional)
- ⚪ Situation Militaire (optional)
- ⚪ Attestation de Travail (optional)

### 4. Applications Page (`/applications`)
**Track your job applications**

| Feature | Description |
|---------|-------------|
| 📋 Application List | All submitted applications |
| 🏷️ Status | Pending ⏳ / Reviewed 👀 / Accepted ✅ / Rejected ❌ |
| 📅 Timeline | Date of application |
| 🔗 Job Details | Link to original job posting |

### 5. Login Page (`/login`)
**User authentication**

| Feature | Description |
|---------|-------------|
| 📧 Email Login | Authenticate with email/password |
| 🔐 JWT Tokens | Secure session management |
| 🔗 Register Link | New user registration |

### 6. Register Page (`/register`)
**Create new account**

| Feature | Description |
|---------|-------------|
| 📝 Registration Form | Name, email, password |
| 👤 Role Selection | Candidate or Recruiter |
| ✅ Validation | Email format, password strength |

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

## 🤖 AI Chatbot Features

The chatbot understands natural language in **3 languages** and responds in the same language:

### French Examples 🇫🇷
- **"Bonjour, je cherche un emploi"** → Greeting + help options
- **"Trouver emplois Python à Alger"** → Search by skill & location
- **"Comment s'inscrire à l'ANEM?"** → Registration FAQ
- **"Conseils pour l'entretien"** → Interview preparation tips

### Arabic Examples 🇩🇿
- **"مرحبا، أبحث عن عمل"** → Greeting in Arabic
- **"وظائف في وهران"** → Jobs in Oran
- **"كيفية التسجيل في ANEM؟"** → Registration FAQ
- **"ما هي الوثائق المطلوبة؟"** → Document requirements

### English Examples 🇬🇧
- **"Hello, I'm looking for a job"** → Greeting + help
- **"Find me Python jobs in Algiers"** → Searches by skill and location
- **"Show me internships"** → Filters by contract type
- **"Apply for job #5"** → Submits application

### Supported Topics
| Topic | Keywords |
|-------|----------|
| Registration | register, inscription, تسجيل |
| Documents | documents, وثائق, papiers |
| Renewal | renew, renouveler, تجديد |
| Training | formation, DAIP, CFI, CTA |
| Entrepreneurship | ANSEJ, ANIS, CNAC |
| Interview | entretien, مقابلة, interview |
| Sectors | IT, santé, BTP, pétrole, etc. |

## 📚 API Endpoints

### Authentication (`/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login (get JWT token) |
| GET | `/auth/me` | Get current user |

### Chat - AI (`/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send message (authenticated) |
| POST | `/chat/guest` | Send message (guest mode) |
| GET | `/chat/history` | Get chat history |

### Jobs (`/jobs`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | List all jobs |
| GET | `/jobs/{id}` | Get job details |
| POST | `/jobs` | Create job (recruiter) |
| PUT | `/jobs/{id}` | Update job |
| DELETE | `/jobs/{id}` | Delete job |

### Applications (`/apply`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/apply` | Apply for job |
| GET | `/apply` | My applications |
| PUT | `/apply/{id}/status` | Update status (recruiter) |

### Documents/Dossier (`/documents`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/documents/requirements` | List required documents |
| GET | `/documents/my-dossier` | Get user's dossier status |
| GET | `/documents` | List user's documents |
| POST | `/documents` | Submit a document |
| GET | `/documents/{id}` | Get document details |
| DELETE | `/documents/{id}` | Delete document |
| PATCH | `/documents/{id}/review` | Review document (admin) |
| GET | `/documents/admin/pending` | Pending documents (admin) |

### Profile (`/profile`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profile` | Get user profile |
| PUT | `/profile` | Update profile |

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
> The system follows a **Layered Microservice-Oriented Architecture** integrating an AI service for natural language understanding with multilingual support for the Algerian context.

### Key Features
1. **Separation of Concerns** - Each layer has specific responsibilities
2. **AI Integration** - Natural language processing for job search (FR/AR/EN)
3. **Multilingual Support** - Full French, Arabic, English with RTL
4. **Algeria-Specific** - 58 Wilayas, ANEM programs (DAIP, CFI, CTA)
5. **Document Tracking** - ANEM registration dossier management
6. **Scalable Design** - Modular components
7. **Modern Web Stack** - FastAPI, React, Tailwind CSS

### Technologies Used
| Layer | Technology |
|-------|------------|
| **Frontend** | React.js, Tailwind CSS, Vite |
| **Backend** | FastAPI, Python 3.10+ |
| **Database** | SQLAlchemy (PostgreSQL/SQLite) |
| **AI** | OpenAI API (GPT-3.5/4) + Local NLP |
| **Auth** | JWT tokens, bcrypt |
| **i18n** | Custom LanguageContext (FR/AR/EN) |

### Database Models
```
User          → Jobs, Applications, Documents, ChatMessages
Job           → Applications
Application   → Job, User (candidate)
Document      → User (dossier tracking)
ChatMessage   → User (conversation history)
```

## 🌐 Multilingual Support

The platform supports 3 languages with automatic detection:

| Feature | French | Arabic | English |
|---------|--------|--------|---------|
| UI Labels | ✅ | ✅ (RTL) | ✅ |
| Chatbot | ✅ | ✅ | ✅ |
| ANEM FAQ | ✅ | ✅ | ✅ |
| Wilayas | ✅ | ✅ | ✅ |
| Documents | ✅ | ✅ | ✅ |

### Language Detection
- **Arabic**: Detects Arabic Unicode characters (ء-ي)
- **French**: Common words (bonjour, cherche, emploi, je, etc.)
- **English**: Common words (hello, find, job, the, etc.)
- **Default**: French (for Algeria)

## 📄 License

MIT License - Free for academic use
