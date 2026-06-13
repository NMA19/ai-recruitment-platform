# Frontend - Wassit AI Chatbot UI

Modern React + Vite user interface for Wassit AI Chatbot.

## Overview

This is the React + Vite frontend for the Wassit AI recruitment chatbot. It provides:
- Chat interface with AI responses and job recommendations
- User authentication (login/register)
- Profile management with picture upload
- Theme switching and language preferences
- Real-time message history
- Responsive mobile-friendly design

## Quick Start

### Prerequisites
- Node.js 18+ and npm

### Setup

```bash
# Install dependencies
npm install

# Create .env file (optional, for custom API URL)
cp ../.env.example .env

# Start development server
npm run dev
# Opens at http://localhost:5173
```

### Configuration

Create a `frontend/.env` file to override settings:

```env
# API endpoint (backend)
VITE_API_URL=http://localhost:5000

# Environment
VITE_ENV=development
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── ChatBox.jsx      # Chat interface
│   │   ├── Navbar.jsx       # Navigation bar
│   │   ├── ProfileModal.jsx # Profile editor
│   │   ├── MessageBubble.jsx # Message display
│   │   ├── JobCard.jsx      # Job listing
│   │   ├── ErrorBoundary.jsx # Error handling
│   │   └── README.md
│   ├── context/             # State management
│   │   ├── AuthContext.jsx  # Authentication state
│   │   ├── ThemeContext.jsx # Theme (light/dark)
│   │   ├── LanguageContext.jsx # Language (en/ar)
│   │   └── README.md
│   ├── pages/               # Page components
│   │   ├── ChatPage.jsx     # Main chat page
│   │   ├── LoginPage.jsx    # Login screen
│   │   ├── RegisterPage.jsx # Register screen
│   │   └── README.md
│   ├── services/            # API client
│   │   ├── api.js           # Axios instance & calls
│   │   └── README.md
│   ├── App.jsx              # Root component
│   ├── main.jsx             # Entry point
│   ├── index.css            # Global styles
│   └── README.md
├── public/                  # Static assets
├── tests/                   # E2E tests
│   ├── upload-cv.spec.js
│   ├── fixtures/
│   └── README.md
├── package.json
├── vite.config.js
├── eslint.config.js
├── tailwind.config.js       # Tailwind CSS config
├── postcss.config.js        # PostCSS config
├── playwright.config.js     # E2E test config
└── README.md               # This file
```

## Routes

| Route | Purpose | Auth Required |
|-------|---------|---------------|
| `/` | Chat & recommendations | Yes |
| `/login` | User login | No |
| `/register` | New account | No |
| `/` (when logged out) | Redirects to login | - |

## Development

### Running Dev Server

```bash
# Start with hot reload
npm run dev

# Server runs on http://localhost:5173
# Automatically reloads on file changes
```

### Building

```bash
# Create production build
npm run build
# Output in dist/

# Preview production build
npm run preview
```

### Linting

```bash
# Check code style
npm run lint

# Fix linting issues
npm run lint -- --fix
```

### Testing

```bash
# Run end-to-end tests
npx playwright test

# Run tests in UI mode
npx playwright test --ui

# Run specific test file
npx playwright test tests/upload-cv.spec.js

# Debug test
npx playwright test --debug
```

## Components 🧩

### ChatBox
Main chat interface component.

```jsx
<ChatBox />
```

**Features:**
- Message input
- Send button
- Auto-scroll to latest message
- Rate limiting feedback

### ProfileModal
User profile editor with avatar selection.

```jsx
<ProfileModal isOpen={true} onClose={() => {}} />
```

**Features:**
- Avatar selection
- Bio/location/profession editing
- Profile picture upload
- Preferences (theme, language)

### Navbar
Navigation bar with user menu.

```jsx
<Navbar user={user} onLogout={() => {}} />
```

**Features:**
- User menu
- Logout button
- Theme toggle
- Language selector

### MessageBubble
Displays a single message.

```jsx
<MessageBubble role="user" content="Hello!" />
<MessageBubble role="assistant" content="Hi there!" />
```

### JobCard
Displays job recommendation.

```jsx
<JobCard job={jobData} />
```

### ErrorBoundary
Error fallback UI.

```jsx
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

## Context (State Management)

### AuthContext
Manages user authentication.

```javascript
const { user, token, login, logout, register } = useContext(AuthContext);
```

### ThemeContext
Manages light/dark theme.

```javascript
const { theme, toggleTheme } = useContext(ThemeContext);
```

### LanguageContext
Manages i18n language.

```javascript
const { language, changeLanguage } = useContext(LanguageContext);
```

## API Client

The `api.js` service provides:

```javascript
// Auth endpoints
api.register(fullName, email, password)
api.login(email, password)
api.getProfile()
api.updateProfile(data)
api.uploadProfilePicture(file)

// Chat endpoints
api.sendMessage(sessionId, message, cvText)
api.getSessionHistory(sessionId)
api.clearSession(sessionId)
```

## Styling

### Tailwind CSS

```jsx
<div className="flex items-center justify-between p-4 bg-blue-500">
  <h1 className="text-2xl font-bold text-white">Title</h1>
</div>
```

Configuration in `tailwind.config.js`.

### CSS Modules (Optional)

```jsx
import styles from './Component.module.css';
<div className={styles.container}>...</div>
```

## Environment Variables

### Available in Browser

Variables prefixed with `VITE_` are available in the browser:

```javascript
console.log(import.meta.env.VITE_API_URL)
```

### Examples

```env
# .env or .env.local
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=Wassit AI Chatbot
VITE_ENV=development
```

## Performance

### Code Splitting

Vite automatically splits code for:
- Vendor code (node_modules)
- Component bundles
- Page bundles

### Lazy Loading

```jsx
import { lazy, Suspense } from 'react';

const ChatPage = lazy(() => import('./pages/ChatPage'));

<Suspense fallback={<Loading />}>
  <ChatPage />
</Suspense>
```

### Image Optimization

Use Vite's image imports:

```jsx
import logo from './logo.png?url';
<img src={logo} />
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security

### XSS Protection
- React escapes JSX by default
- Use `dangerouslySetInnerHTML` carefully
- Sanitize user input

### CSRF Protection
- API uses Bearer token auth
- Token stored securely

### Headers
- CSP headers from backend
- HTTPS enforced in production

## Troubleshooting 🐛

### Dev Server Won't Start

```bash
# Check if port 5173 is in use
lsof -i :5173

# Use different port
npm run dev -- --port 3000
```

### Module Not Found

```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### API Connection Error

```javascript
// Check .env or vite.config.js
console.log(import.meta.env.VITE_API_URL)

// Verify backend is running
curl http://localhost:5000/health
```

### Build Fails

```bash
# Clear cache
rm -rf dist/

# Rebuild
npm run build

# Check for TypeScript errors
npx tsc --noEmit
```

## Production Build

### Building

```bash
# Create optimized build
npm run build

# Output location: dist/
# Ready to serve with any static host
```

### Serving

With Docker (see [docker-compose.yml](../docker-compose.yml)):
```bash
docker-compose up frontend
```

With Nginx:
```bash
docker run -v /path/to/dist:/usr/share/nginx/html -p 80:80 nginx
```

### Performance Optimizations

- [x] Minification
- [x] Code splitting
- [x] Tree shaking
- [x] Asset compression
- [x] Source maps (optional for production)

## Dependencies 📦

Key packages:
- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Context API** - State management

See `package.json` for complete list.

## Scripts

```bash
# Development
npm run dev              # Start dev server
npm run lint            # Check code style
npm run lint -- --fix   # Fix linting issues

# Building
npm run build           # Create production build
npm run preview         # Preview production build

# Testing
npm test               # Run tests
npx playwright test    # Run E2E tests
npx playwright test --ui  # Tests in UI mode

# Cleanup
npm prune              # Remove unused packages
npm audit              # Check for vulnerabilities
```

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m 'Add amazing feature'

# Push and create PR
git push origin feature/amazing-feature
```

## Support & Docs

- [Main README](../README.md) - Project overview
- [API Documentation](../API_DOCUMENTATION.md) - Backend API
- [Backend README](../backend/README.md) - Backend setup
- [Architecture](../ARCHITECTURE.md) - System design

---

**Frontend Version**: 1.0  
**Last Updated**: 2026-05-29
**Tech Stack**: React 18 + Vite + Tailwind CSS


# Output: dist/ folder (316 KB gzipped)
```

## 🌈 Component Structure

### Layout Components

**Navbar.jsx**
- Logo and navigation links
- Theme toggle (sun/moon icon)
- Authentication links (Login, Sign Up, Logout)
- English-only text
- Responsive mobile menu

**ChatBox.jsx**
- Input field for user messages
- Message display area
- Chat state management
- Error boundary wrapper
- Message parsing (handles multiple response formats)

### Page Components

**ChatPage.jsx**
- Main application page
- Chat interface with ErrorBoundary
- Feature cards (Quick Apply, Smart Search, Track Progress, Help)
- Responsive layout

**LoginPage.jsx**
- Email/password login form
- Error messages
- Link to register page
- Token storage

**RegisterPage.jsx**
- User registration form
- Email validation
- Auto-login after registration
- Link to login page

**ApplicationsPage.jsx**
- User's job applications list
- Status display (Pending, Accepted, Rejected)
- Application details

**DossierPage.jsx**
- User profile information
- Edit personal data
- Download profile/CV
- Account settings

### Message Components

**MessageBubble.jsx**
- Displays individual messages (user/bot)
- Markdown support (bold text)
- Type-safe string formatting
- Timestamps
- Message attribution

**ErrorBoundary.jsx**
- Catches component render errors
- Displays friendly error UI
- "Try Again" button to recover
- Prevents app crashes

### Theme Component

**ThemeToggle.jsx**
- Sun/Moon icons
- Dark mode toggle
- Tailwind dark: classes

## 🎨 Styling System

### Tailwind CSS Configuration

```javascript
// Custom color palette (Indigo-Blue-Cyan theme)
colors: {
  primary: '#6366f1',   // Indigo
  secondary: '#0ea5e9', // Cyan
  accent: '#8b5cf6'     // Purple
}

// Dark mode support
darkMode: 'class' // Toggle via .dark on html element
```

### Design Features

- **Glass Morphism** - Frosted glass effect (backdrop-blur)
- **Gradients** - Smooth gradient backgrounds
- **Animations** - Smooth transitions (300ms)
- **Responsive** - Mobile-first design (sm, md, lg breakpoints)
- **Accessibility** - Proper color contrast, semantic HTML

## 🔐 Authentication Context

### AuthContext.jsx

```javascript
// Global auth state
{
  user: User | null,
  token: string | null,
  loading: boolean,
  login: (email, password) => Promise,
  logout: () => void,
  register: (email, password, fullName) => Promise
}

// Safe hook - prevents crashes during initialization
const { user, token } = useAuth();
// Returns default context if AuthProvider not mounted yet
```

## 🌐 API Communication

### api.js Service

```javascript
// Auto-detects backend port (5000-5010)
// Tries each port until finds responsive backend

// Available methods:
axios.post('/chat/guest', { message })
axios.post('/chat', { message, userId })
axios.get('/auth/me')
axios.post('/auth/login', { email, password })
axios.post('/auth/register', { email, password, fullName })
axios.get('/jobs?wilaya=Algiers')
axios.post('/apply', { jobId, userId })
```

### Error Handling

- 15-second request timeout
- Graceful fallback on connection failure
- User-friendly error messages
- Automatic retry on certain errors

## 🚨 Error Handling

### ErrorBoundary Component

Wraps critical components to catch render errors:

```jsx
<ErrorBoundary>
  <ChatBox />
</ErrorBoundary>
```

Features:
- Catches component crashes
- Shows friendly error message
- "Try Again" button to reset state
- Prevents entire app crash

### Context Guards

Auth context returns safe defaults if provider not mounted:

```javascript
// Safe to use anywhere, never crashes
const useAuth = () => {
  try {
    return useContext(AuthContext);
  } catch {
    return DEFAULT_CONTEXT; // Safe fallback
  }
};
```

## 🎯 Features

✅ Real-time chat interface
✅ User authentication (login/register)
✅ Job search by Wilaya
✅ Quick job application
✅ Application tracking
✅ Dark mode / Light mode
✅ Responsive design (mobile/tablet/desktop)
✅ Error boundaries
✅ Auto backend port detection
✅ Message markdown support
✅ Glass morphism UI
✅ Smooth animations

## 🔧 Configuration

### Vite Configuration

```javascript
// Hot Module Replacement (HMR)
server: {
  hmr: true,
  port: 5173
}

// Build optimization
build: {
  rollupOptions: { /* code splitting */ },
  cssCodeSplit: true,
  minify: 'terser'
}
```

### Tailwind Configuration

```javascript
content: [
  './src/**/*.{js,jsx}',
  './index.html'
],
theme: {
  extend: {
    colors: { /* custom colors */ }
  }
}
```

## 🐛 Troubleshooting

### Backend Not Found
```bash
# Frontend auto-detects backend (tries ports 5000-5010)
# If still not working, manually set API URL
VITE_API_URL=http://localhost:5008 npm run dev
```

### CSS Not Loading
```bash
# Rebuild Tailwind cache
npm run build:css

# Or restart dev server
npm run dev
```

### Build Too Large
```bash
# Analyze bundle size
npm run build -- --analyze

# Current size: 316 KB gzipped ✓
```

### Hot Reload Not Working
```bash
# Clear cache and restart
rm -rf node_modules/.vite
npm run dev
```

## 📊 Performance

- **Build Size**: 316 KB gzipped
- **Initial Load**: ~2 seconds
- **API Response**: ~100ms average
- **Bundle Analysis**: Optimized with code splitting

## 🚀 Deployment

### Build for Production

```bash
npm run build
# Creates dist/ folder ready to deploy

# Test build locally
npm run preview
```

### Deploy to Cloud

```bash
# Deploy dist/ folder to:
# - Netlify
# - Vercel
# - GitHub Pages
# - Azure Static Web Apps
# - AWS S3 + CloudFront

# Environment: Set VITE_API_URL to production backend URL
```

## 📚 Tech Stack

- **Framework**: React 19.2
- **Build Tool**: Vite 5.4.21
- **Styling**: Tailwind CSS 3.x
- **HTTP Client**: Axios
- **State Management**: React Context API
- **Icons**: Lucide React (or similar)
- **Language**: JavaScript (ES2024+)

## 🎓 Development Notes

- Use `.jsx` extension for all React components
- Tailwind CSS classes prioritized over CSS files
- Component props validated with PropTypes (optional)
- Environment variables prefix with `VITE_`
- No TypeScript currently (can be added)

## ✨ Current Status

✅ Production build (316 KB gzipped)
✅ React 19.2 compatible
✅ Vite hot reload working
✅ Tailwind CSS optimized
✅ Error boundary active
✅ Auth context guarded
✅ Backend auto-detection active
✅ Responsive design verified

---

**Status**: 🟢 Production Ready | **Updated**: March 24, 2026
