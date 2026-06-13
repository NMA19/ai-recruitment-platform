/**
 * ChatBox Component
 * The main chat interface component
 */

import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Loader2, Sparkles, RefreshCw, LogIn, Globe } from 'lucide-react';
import MessageBubble from './MessageBubble';
import JobCard from './JobCard';
import { chatAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useChat } from '../context/ChatContext';
import { useLanguage } from '../context/LanguageContext';

export default function ChatBox() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      text: "Hello! 👋 I'm your AI recruitment assistant. I can help you find jobs, apply for positions, and track your applications. What are you looking for?",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [atBottom, setAtBottom] = useState(true);
  const [showLoginPrompt, setShowLoginPrompt] = useState(false);
  const { user, isAuthenticated } = useAuth();
  const { anonymousRequestCount, incrementAnonymousRequest, resetAnonymousRequestCount } = useChat();
  const { communicationLanguage, setCommunicationLanguage, updateLanguageFromInput, languageNames, detectLanguage } = useLanguage();
  const [sessionId] = useState(() => {
    // Use user email as session ID for per-user chat history
    if (user?.email) {
      return `session_${user.email}`;
    }
    // Fallback to browser session if not logged in
    const existing = localStorage.getItem('requai_session_id') || localStorage.getItem('wassit_session_id');
    if (existing) return existing;
    const next = `session_${Date.now()}`;
    localStorage.setItem('requai_session_id', next);
    return next;
  });
  const messagesEndRef = useRef(null);
  const messageListRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleMessageScroll = () => {
    const container = messageListRef.current;
    if (!container) return;

    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    setAtBottom(distanceFromBottom < 120);
  };

  useEffect(() => {
    if (atBottom) {
      scrollToBottom();
    }
  }, [messages]);

  // Clear chat when user logs out
  useEffect(() => {
    if (!isAuthenticated && messages.length > 1) {
      setMessages([
        {
          id: 1,
          type: 'bot',
          text: "Hello! 👋 I'm your AI recruitment assistant. I can help you find jobs, apply for positions, and track your applications. What are you looking for?",
          timestamp: new Date(),
        }
      ]);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    let cancelled = false;

    const loadHistory = async () => {
      try {
        const response = await chatAPI.getHistory(sessionId);
        const history = response.data?.history || [];
        if (cancelled || history.length === 0) return;

        const loadedMessages = history.map((entry, index) => {
          return {
            id: `${sessionId}-${index}`,
            type: entry.role === 'assistant' ? 'bot' : 'user',
            text: entry.content || entry.response || '',
            jobs: normalizeJobs(entry.jobs),
            intent: entry.intent,
            confidence: entry.confidence,
            entities: entry.entities,
            behavior: entry.behavior,
            security: entry.security,
            timestamp: entry.timestamp || new Date().toISOString(),
          };
        });

        setMessages([
          {
            id: 1,
            type: 'bot',
            text: "Hello! 👋 I'm your AI recruitment assistant. I can help you find jobs, apply for positions, and track your applications. What are you looking for?",
            timestamp: new Date(),
          },
          ...loadedMessages,
        ]);
      } catch (error) {
        console.warn('Could not load chat history:', error.message);
      }
    };

    loadHistory();

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    // Check anonymous request limit
    if (!isAuthenticated && anonymousRequestCount >= 3) {
      setShowLoginPrompt(true);
      return;
    }

    // Detect language from input
    const detectedLang = updateLanguageFromInput(input);

    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: input,
      timestamp: new Date(),
      language: detectedLang,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Increment anonymous request counter if not authenticated
      if (!isAuthenticated) {
        incrementAnonymousRequest();
      } else {
        // Reset counter when user logs in
        resetAnonymousRequestCount();
      }

      // Build conversation history for context (only previous messages, not current input)
      const conversationHistory = messages
        .filter(m => m.type === 'user' || m.type === 'bot')
        .map(m => ({
          role: m.type === 'bot' ? 'assistant' : 'user',
          content: m.text,
        }));

      const response = await chatAPI.sendMessage(input, sessionId, null, false, user?.email, detectedLang, conversationHistory);

      const data = response.data;

      const responseText =
        typeof data.response === 'string'
          ? data.response
          : typeof data.answer === 'string'
            ? data.answer
            : data.message || 'I found matching opportunities for you.';

      const normalizedJobs = normalizeJobs(data.jobs);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: responseText,
        jobs: normalizedJobs,
        intent: data.intent,
        confidence: data.confidence,
        entities: data.entities,
        behavior: data.behavior,
        security: data.security,
        timestamp: new Date(),
        language: detectedLang,
      };

      setMessages(prev => [...prev, botMessage]);

      // Show login prompt after 3rd request for anonymous users
      if (!isAuthenticated && anonymousRequestCount >= 3) {
        setTimeout(() => {
          setShowLoginPrompt(true);
        }, 1500);
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: "Sorry, I'm having trouble connecting. Please try again.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // CV upload handlers
  const fileInputRef = useRef(null);
  const handleUploadClick = () => fileInputRef.current?.click();
  const handleFileChange = async (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    setLoading(true);
    try {
      // show a user message about upload
      setMessages(prev => [...prev, { id: Date.now(), type: 'user', text: `Uploaded CV: ${file.name}`, timestamp: new Date(), language: communicationLanguage }]);
      const resp = await chatAPI.uploadCV(file, sessionId, false, user?.email, communicationLanguage);
      const data = resp.data;
      const responseText = data.response || 'CV processed. Here are matching jobs.';
      const normalizedJobs = normalizeJobs(data.jobs);
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        text: responseText,
        jobs: normalizedJobs,
        timestamp: new Date(),
        language: communicationLanguage,
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('CV upload failed', err);
      setMessages(prev => [...prev, { id: Date.now()+2, type: 'bot', text: 'CV upload failed. Try again or paste your CV text.', timestamp: new Date(), language: communicationLanguage }]);
    } finally {
      setLoading(false);
      // clear input value to allow re-uploading same file if needed
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="relative flex flex-col h-full bg-gradient-to-b from-white to-gray-50 dark:from-slate-800 dark:to-slate-900 backdrop-blur-sm rounded-2xl shadow-2xl border border-gray-100/50 dark:border-slate-700/50 overflow-hidden">
      {/* Chat Header */}
      <div className="relative bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 px-6 py-5 shadow-lg">
        <div className="absolute inset-0 opacity-20 bg-black"></div>
        <div className="relative flex items-center space-x-4">
          <div className="w-12 h-12 bg-white/25 backdrop-blur-md rounded-xl flex items-center justify-center shadow-lg">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-white text-xl font-bold tracking-tight">Requ-AI Chat</h2>
            <p className="text-blue-100 text-xs font-medium tracking-wide">AI-powered job recommendations</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-2 text-[11px] text-white/90 bg-white/10 px-3 py-1.5 rounded-full backdrop-blur">
              <RefreshCw className="w-3 h-3" />
              <span className="font-semibold">Live</span>
            </div>
            {/* Language Badge */}
            <div className="flex items-center gap-1.5 text-[11px] text-white bg-white/20 px-3 py-1.5 rounded-full backdrop-blur border border-white/30">
              <Globe className="w-3 h-3" />
              <span className="font-semibold">{languageNames[communicationLanguage] || 'English'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Prompts */}
      <div className="px-5 pt-4 pb-3 bg-gradient-to-b from-white/50 to-white/30 dark:from-slate-800/50 dark:to-slate-900/30 border-b border-gray-100 dark:border-slate-700">
        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400 mb-2.5">Quick prompts</p>
        <div className="flex flex-wrap gap-2">
          <QuickPrompt onClick={() => setInput('Find Python jobs in Algiers')} label="Python in Algiers" />
          <QuickPrompt onClick={() => setInput('Show jobs for backend developers')} label="Backend roles" />
          <QuickPrompt onClick={() => setInput('I want remote or hybrid work')} label="Remote / hybrid" />
        </div>
      </div>

      {/* Messages Container */}
      <div
        ref={messageListRef}
        onScroll={handleMessageScroll}
        className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900/50 scroll-smooth"
      >
        {messages.map((message) => (
          <div key={message.id} className="animate-fade-in-up">
            <MessageBubble message={message} />
            
            {/* Job Cards */}
            {message.jobs && message.jobs.length > 0 && (
              <div className="mt-3 space-y-3 ml-12">
                <div className="flex items-center justify-between pr-1">
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-indigo-600 dark:text-indigo-300">
                    Top recommendations
                  </p>
                  <span className="text-[11px] text-gray-500 dark:text-gray-400">
                    {message.jobs.length} matches
                  </span>
                </div>
                {message.jobs.map((job) => (
                  <JobCard key={job.id} job={job} />
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400 ml-12">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-dot"></div>
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-dot"></div>
              <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full typing-dot"></div>
            </div>
            <span className="text-sm">AI is thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {!atBottom && (
        <button
          type="button"
          onClick={scrollToBottom}
          className="absolute bottom-24 right-6 z-20 inline-flex items-center gap-2 rounded-full bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-indigo-500/30 hover:bg-indigo-700"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Latest message
        </button>
      )}

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-5 bg-gradient-to-b from-white/80 to-gray-50/80 dark:from-slate-800/80 dark:to-slate-900/80 border-t border-gray-100 dark:border-slate-700 backdrop-blur-sm">
        {/* Anonymous request warning */}
        {!isAuthenticated && anonymousRequestCount > 0 && anonymousRequestCount <= 3 && (
          <div className="mb-3 px-4 py-2 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-700/50 rounded-lg">
            <p className="text-xs text-amber-800 dark:text-amber-300 font-semibold">
              Free trial: {3 - anonymousRequestCount} request{3 - anonymousRequestCount !== 1 ? 's' : ''} remaining
            </p>
          </div>
        )}
        <div className="mb-3 text-[10px] leading-relaxed font-semibold uppercase tracking-[0.15em] text-gray-500 dark:text-gray-400">
          💡 Tip: Upload a PDF CV or ask about jobs, skills, salary, and locations
        </div>
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2.5">
            <div className="flex-1 relative group">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask for jobs, skills, salary, or location..."
                className="w-full px-5 py-4 bg-white dark:bg-slate-700/50 dark:text-white border-2 border-gray-200 dark:border-slate-600 rounded-xl focus:outline-none focus:border-indigo-500 dark:focus:border-indigo-400 focus:shadow-lg focus:shadow-indigo-500/20 transition-all placeholder-gray-400 dark:placeholder-gray-500 font-medium"
                disabled={loading}
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-300 dark:text-gray-600 group-focus-within:text-indigo-500 transition-colors">
                {loading && <Loader2 className="w-5 h-5 animate-spin" />}
              </div>
            </div>
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-4 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-xl hover:from-indigo-700 hover:to-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-indigo-500/40 disabled:shadow-none font-semibold flex items-center justify-center"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
            
            {/* CV upload button */}
            <input ref={fileInputRef} onChange={handleFileChange} type="file" accept="application/pdf" className="hidden" data-testid="cv-upload-input" />
            <button 
              type="button" 
              onClick={handleUploadClick} 
              disabled={loading} 
              className="px-5 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl hover:from-emerald-700 hover:to-teal-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-emerald-500/40 disabled:shadow-none font-semibold" 
              data-testid="cv-upload-button"
            >
              📄
            </button>
          </div>
        </div>
      </form>

      {/* Login Prompt Modal */}
      {showLoginPrompt && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in-up">
          <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 border border-gray-100 dark:border-slate-700 animate-scale-in">
            {/* Icon */}
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
              <LogIn className="w-8 h-8 text-white" />
            </div>

            {/* Content */}
            <h3 className="text-xl font-bold text-center text-gray-900 dark:text-white mb-2">
              Free Trial Limit Reached
            </h3>
            <p className="text-center text-gray-600 dark:text-gray-300 text-sm mb-6">
              You've used all 3 free chat requests. Sign in or create an account to continue exploring job opportunities!
            </p>

            {/* Benefits */}
            <div className="bg-indigo-50 dark:bg-indigo-900/30 rounded-lg p-4 mb-6 border border-indigo-200 dark:border-indigo-700/50">
              <p className="text-xs font-semibold text-indigo-900 dark:text-indigo-300 mb-2">✨ With an account:</p>
              <ul className="space-y-1 text-xs text-indigo-800 dark:text-indigo-400">
                <li>✓ Unlimited chat requests</li>
                <li>✓ Save job preferences</li>
                <li>✓ Track applications</li>
              </ul>
            </div>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowLoginPrompt(false)}
                className="flex-1 px-4 py-3 bg-gray-100 dark:bg-slate-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-200 dark:hover:bg-slate-600 transition-all font-semibold text-sm"
              >
                Cancel
              </button>
              <button
                onClick={() => navigate('/login')}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-lg hover:from-indigo-700 hover:to-blue-700 transition-all font-semibold text-sm shadow-lg hover:shadow-indigo-500/40"
              >
                Sign In
              </button>
            </div>

            {/* Register link */}
            <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-4">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/register')}
                className="text-indigo-600 dark:text-indigo-400 font-semibold hover:underline"
              >
                Create one
              </button>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

function QuickPrompt({ label, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="px-4 py-2 rounded-full border-2 border-indigo-300 dark:border-indigo-700 bg-gradient-to-r from-indigo-50 to-blue-50 dark:from-indigo-900/40 dark:to-blue-900/40 text-indigo-700 dark:text-indigo-300 hover:from-indigo-100 hover:to-blue-100 dark:hover:from-indigo-900/60 dark:hover:to-blue-900/60 transition-all font-semibold text-sm shadow-sm hover:shadow-md"
    >
      {label}
    </button>
  );
}

function normalizeJob(job) {
  return {
    id: job.id || `${job.jobId || job['Job Title'] || job.title || 'job'}-${job.company || job['Company'] || 'company'}`,
    jobTitle: job.jobTitle || job['Job Title'] || job.title || 'Recommended role',
    company: job.company || job['Company'] || 'Anonymous company',
    location: job.location || job['location'] || 'Algeria',
    workType: job['Work Type'] || job.workType || 'Full-time',
    experience: job.Experience || job.experience || 'Not specified',
    salaryRange: job['Salary Range'] || job.salaryRange || formatSalary(job.salary_dzd),
    skills: Array.isArray(job.skills) ? job.skills : splitSkills(job.skills),
    matchScore: typeof job.match_score === 'number' ? job.match_score : null,
    raw: job,
  };
}

function normalizeJobs(jobs) {
  if (!Array.isArray(jobs)) return [];
  return jobs.map(normalizeJob);
}

function splitSkills(skills) {
  if (!skills) return [];
  if (Array.isArray(skills)) return skills;
  return String(skills)
    .split(/[,|]/)
    .map((skill) => skill.trim())
    .filter(Boolean);
}

function formatSalary(value) {
  if (!value && value !== 0) return 'Salary on request';
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return String(value);
  if (numeric >= 1000) return `${Math.round(numeric).toLocaleString('en-US')} DZD`;
  return `${Math.round(numeric * 1000).toLocaleString('en-US')} DZD`;
}
