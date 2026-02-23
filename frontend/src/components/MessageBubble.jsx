/**
 * MessageBubble Component
 * Displays individual chat messages
 */

import { Bot, User } from 'lucide-react';

export default function MessageBubble({ message }) {
  const isBot = message.type === 'bot';

  return (
    <div className={`flex items-start space-x-3 ${!isBot ? 'flex-row-reverse space-x-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isBot ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-600'
      }`}>
        {isBot ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
      </div>

      {/* Message Bubble */}
      <div className={`max-w-[75%] ${isBot ? '' : 'text-right'}`}>
        <div className={`inline-block px-4 py-2.5 rounded-2xl ${
          isBot 
            ? 'bg-white shadow-sm border border-gray-100 text-gray-800' 
            : 'bg-blue-600 text-white'
        }`}>
          {/* Format message text with markdown-like support */}
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {formatMessage(message.text)}
          </div>
        </div>
        
        {/* Timestamp */}
        <div className={`text-xs text-gray-400 mt-1 ${isBot ? '' : 'text-right'}`}>
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
