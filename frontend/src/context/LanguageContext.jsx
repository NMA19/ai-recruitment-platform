/**
 * Language Context
 * Auto-detects language from user input and manages communication language
 */

import { createContext, useContext, useState } from 'react';

// Simple language detection based on character patterns
const detectLanguageFromText = (text) => {
  if (!text || text.length === 0) return 'en';
  
  // Arabic script detection
  const arabicRegex = /[\u0600-\u06FF]/g;
  // Russian/Cyrillic detection
  const cyrillicRegex = /[\u0400-\u04FF]/g;
  // Chinese detection
  const chineseRegex = /[\u4E00-\u9FFF]/g;
  // Japanese hiragana/katakana
  const japaneseRegex = /[\u3040-\u309F\u30A0-\u30FF]/g;
  // Korean hangul
  const koreanRegex = /[\uAC00-\uD7AF]/g;

  const matches = {
    ar: (text.match(arabicRegex) || []).length,
    ru: (text.match(cyrillicRegex) || []).length,
    zh: (text.match(chineseRegex) || []).length,
    ja: (text.match(japaneseRegex) || []).length,
    ko: (text.match(koreanRegex) || []).length,
  };

  // Find which language has the most characters
  const maxMatches = Math.max(...Object.values(matches));
  if (maxMatches > 0) {
    for (const [lang, count] of Object.entries(matches)) {
      if (count === maxMatches) return lang;
    }
  }

  const lowered = text.toLowerCase();
  const frenchHints = [
    'emploi', 'travail', 'recrutement', 'poste', 'salaire', 'candidat',
    'candidature', 'entreprise', 'offre', 'contrat', 'expérience',
    'formation', 'diplôme', 'compétence', 'stage', 'télétravail',
    'je cherche', 'je veux',
  ];
  if (frenchHints.some((hint) => lowered.includes(hint))) return 'fr';

  const darijaHints = [
    'khdma', 'khedma', 'khadma', 'nekhdem', 'nheb', 'baghi', 'bghit',
    'chghol', 'setif', 'staif', 'dz',
  ];
  const words = lowered.split(/\s+/);
  if (darijaHints.some((hint) => words.includes(hint))) return 'ar';

  // Default to English
  return 'en';
};

const LanguageContext = createContext(null);

// All 48 Algerian Wilaya
export const WILAYAS = [
  'Adrar', 'Chlef', 'Laghouat', 'Oum El Bouaghi', 'Batna', 'Béjaïa', 'Biskra', 'Béchar',
  'Blida', 'Bouira', 'Tamanrasset', 'Tébessa', 'Tlemcen', 'Tiaret', 'Tizi Ouzou', 'Alger',
  'Djelfa', 'Jijel', 'Sétif', 'Saïda', 'Skikda', 'Sidi Bel Abbès', 'Annaba', 'Guelma',
  'Constantine', 'Médéa', 'Mostaganem', "M'Sila", 'Mascara', 'Ouargla', 'Oran', 'El Bayadh',
  'Illizi', 'Bordj Bou Arreridj', 'Boumerdès', 'El Tarf', 'Tindouf', 'Tissemsilt', 'El Oued',
  'Khenchela', 'Souk Ahras', 'Tipaza', 'Mila', 'Aïn Defla', 'Naâma', 'Aïn Témouchent',
  'Ghardaïa', 'Relizane', 'Drâa Tafilalet', 'Touggourt'
];

// Job sectors (English only)
export const SECTORS = [
  'Information Technology',
  'Healthcare',
  'Education',
  'Construction',
  'Finance & Banking',
  'Telecommunications',
  'Agriculture',
  'Energy & Oil',
  'Manufacturing',
  'Commerce & Sales',
  'Tourism & Hotels',
  'Transport & Logistics',
  'Administration',
  'Engineering',
  'Media & Communication',
];

// English translations (no language switching)
const translations = {
  nav: {
    chat: 'Chat',
    applications: 'My Applications',
    login: 'Login',
    register: 'Sign Up',
    logout: 'Logout',
  },
  chat: {
    welcome: 'Welcome to Requ-AI',
    subtitle: 'Your ANEM career assistant',
    placeholder: "Type your message... (e.g., 'Jobs in Oran')",
    aiThinking: 'AI is thinking...',
  },
  applications: {
    title: 'My Applications',
    subtitle: 'Track Your Progress',
  },
  login: {
    title: 'Welcome Back',
    email: 'Email Address',
    password: 'Password',
    submit: 'Sign In',
  },
  register: {
    title: 'Create Account',
    fullName: 'Full Name',
    email: 'Email Address',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    submit: 'Create Account',
  },
  common: {
    loading: 'Loading...',
    save: 'Save',
    cancel: 'Cancel',
  },
};

export function LanguageProvider({ children }) {
  const [communicationLanguage, setCommunicationLanguage] = useState('en');
  const [detectionEnabled, setDetectionEnabled] = useState(true);

  // Detect language from user message
  const detectLanguage = (text) => {
    if (!text || text.trim().length === 0) return 'en';
    try {
      const detected = detectLanguageFromText(text);
      return detected;
    } catch (err) {
      console.warn('Language detection error:', err);
      return communicationLanguage;
    }
  };

  // Update communication language based on detected text
  const updateLanguageFromInput = (text) => {
    if (detectionEnabled && text && text.trim().length > 0) {
      const detected = detectLanguage(text);
      if (detected !== communicationLanguage) {
        setCommunicationLanguage(detected);
        return detected;
      }
    }
    return communicationLanguage;
  };

  // Language display names
  const languageNames = {
    'en': 'English',
    'ar': 'العربية (Arabic)',
    'fr': 'Français (French)',
    'es': 'Español (Spanish)',
    'de': 'Deutsch (German)',
    'it': 'Italiano (Italian)',
    'pt': 'Português (Portuguese)',
    'ru': 'Русский (Russian)',
    'ja': '日本語 (Japanese)',
    'ko': '한국어 (Korean)',
    'zh': '中文 (Chinese)',
  };

  const value = {
    language: 'en', // UI language (always English for now)
    communicationLanguage, // Language for chatbot responses
    setCommunicationLanguage,
    detectLanguage,
    updateLanguageFromInput,
    languageNames,
    detectionEnabled,
    setDetectionEnabled,
    translations,
    t: (key) => {
      const keys = key.split('.');
      let value = translations;
      for (const k of keys) {
        value = value[k];
        if (!value) return key;
      }
      return value;
    },
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
