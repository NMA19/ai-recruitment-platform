/**
 * Chat Context
 * Manages chat state and anonymous request limits
 */

import { createContext, useContext, useState, useCallback } from 'react';

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  const [anonymousRequestCount, setAnonymousRequestCount] = useState(() => {
    const stored = localStorage.getItem('anonymousRequestCount');
    return stored ? parseInt(stored, 10) : 0;
  });

  const clearChat = useCallback(() => {
    // Reset chat state - signal to ChatBox to clear messages
    // This will be triggered on logout or page load
  }, []);

  const incrementAnonymousRequest = useCallback(() => {
    setAnonymousRequestCount(prev => {
      const next = prev + 1;
      localStorage.setItem('anonymousRequestCount', next.toString());
      return next;
    });
  });

  const resetAnonymousRequestCount = useCallback(() => {
    setAnonymousRequestCount(0);
    localStorage.removeItem('anonymousRequestCount');
  });

  const value = {
    anonymousRequestCount,
    incrementAnonymousRequest,
    resetAnonymousRequestCount,
    clearChat,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    return {
      anonymousRequestCount: 0,
      incrementAnonymousRequest: () => {},
      resetAnonymousRequestCount: () => {},
      clearChat: () => {},
    };
  }
  return context;
}
