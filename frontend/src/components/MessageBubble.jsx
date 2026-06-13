/**
 * MessageBubble Component
 * Displays individual chat messages with refined styling
 */

import { Bot, User, Sparkles } from 'lucide-react';

export default function MessageBubble({ message }) {
  const isBot = message.type === 'bot';

  const formatEntityValues = (values) => {
    if (Array.isArray(values)) {
      return values.filter(Boolean).join(', ');
    }

    if (values && typeof values === 'object') {
      return Object.values(values)
        .flatMap((value) => (Array.isArray(value) ? value : [value]))
        .filter(Boolean)
        .join(', ');
    }

    return String(values || '');
  };

  return (
    <div className={`flex items-end gap-3 mb-3 ${!isBot ? 'flex-row-reverse' : ''} animate-fade-in-up`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center shadow-sm ${
        isBot 
          ? 'bg-gradient-to-br from-indigo-500 to-cyan-500 text-white' 
          : 'bg-gradient-to-br from-orange-400 to-rose-500 text-white'
      }`}>
        {isBot ? <Sparkles className="w-5 h-5" /> : <User className="w-5 h-5" />}
      </div>

      {/* Message Bubble */}
      <div className={`flex flex-col max-w-[70%] ${!isBot ? 'items-end' : ''}`}>
        <div className={`px-5 py-3.5 rounded-2xl shadow-md transition-all ${
          isBot 
            ? 'bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-slate-700 rounded-tl-none' 
            : 'bg-gradient-to-br from-indigo-600 to-blue-600 text-white rounded-br-none shadow-lg shadow-indigo-500/30'
        }`}>
          {/* Format message text */}
          <div className={`whitespace-pre-wrap text-sm leading-relaxed font-medium ${
            isBot ? 'font-normal' : ''
          }`}>
            {formatMessage(message.text)}
          </div>
        </div>

        {/* NLP Insights Badge (for bot messages) */}
        {isBot && message.intent && (
          <div className="mt-2.5 flex flex-wrap gap-2 text-[11px]">
            {/* Intent Badge */}
            <div className="inline-flex items-center px-3 py-1.5 rounded-full bg-gradient-to-r from-indigo-100 to-blue-100 dark:from-indigo-900/40 dark:to-blue-900/40 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/50 font-semibold">
              <Sparkles className="w-3.5 h-3.5 mr-1.5" />
              {message.intent.replace('_', ' ').toUpperCase()}
              {message.confidence && (
                <span className="ml-2 text-indigo-500 dark:text-indigo-400 font-bold">
                  {Math.round(message.confidence * 100)}%
                </span>
              )}
            </div>

            {/* Entities */}
            {message.entities && Object.entries(message.entities).map(([type, values]) => {
              const formattedValues = formatEntityValues(values);
              if (!formattedValues) return null;
              return (
                <div key={type} className="inline-flex items-center px-3 py-1.5 rounded-full bg-gradient-to-r from-emerald-100 to-teal-100 dark:from-emerald-900/40 dark:to-teal-900/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800/50 font-semibold">
                  <span className="capitalize">{type}:</span>
                  <span className="ml-1.5">{formattedValues}</span>
                </div>
              );
            })}

            {/* Skills */}
            {message.skills && message.skills.technical && message.skills.technical.length > 0 && (
              <div className="inline-flex items-center px-3 py-1.5 rounded-full bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/40 dark:to-pink-900/40 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-800/50 font-semibold">
                💻 {message.skills.technical.slice(0, 2).join(', ')}
                {message.skills.technical.length > 2 && (
                  <span className="ml-1.5">+{message.skills.technical.length - 2}</span>
                )}
              </div>
            )}
          </div>
        )}
        
        {/* Timestamp */}
        <div className={`text-[11px] text-gray-400 dark:text-gray-500 mt-2 ${isBot ? '' : 'text-right'} font-medium`}>
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}

// Helper to format time
function formatTime(date) {
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Helper to format message text (basic markdown support)
function formatMessage(text) {
  // Ensure text is a string
  if (!text || typeof text !== 'string') {
    return String(text || '');
  }
  
  // Bold text: **text**
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={index} className="font-semibold">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}
