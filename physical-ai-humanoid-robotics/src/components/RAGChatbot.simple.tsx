import React, { useState } from 'react';
import './RAGChatbot.css';

/**
 * Simple RAG Chatbot - Test version
 */
const RAGChatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  if (!isOpen) {
    return (
      <button 
        className="chatbot-float-button" 
        onClick={() => setIsOpen(true)}
        aria-label="Open chat"
        style={{ 
          position: 'fixed',
          bottom: '30px',
          right: '30px',
          zIndex: 9999,
          display: 'block'
        }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
          <path d="M12 2C6.48 2 2 6.48 2 12C2 13.54 2.36 15.02 3.02 16.35L2 22L7.65 20.98C8.98 21.64 10.46 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2Z" />
        </svg>
      </button>
    );
  }

  return (
    <div 
      className="chatbot-container"
      style={{ 
        position: 'fixed',
        bottom: '30px',
        right: '30px',
        zIndex: 9999,
        display: 'flex'
      }}
    >
      <div className="chatbot-header">
        <div className="chatbot-header-content">
          <div className="chatbot-header-left">
            <h3>RAG Chatbot</h3>
          </div>
          <button 
            className="chatbot-close-button" 
            onClick={() => setIsOpen(false)}
            style={{ cursor: 'pointer', fontSize: '20px', border: 'none', background: 'white', color: '#25c2a0' }}
          >
            ×
          </button>
        </div>
      </div>
      <div className="chatbot-messages" style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
        <p>Welcome to RAG Chatbot! This is a test message.</p>
        <p style={{ fontSize: '12px', color: '#999', marginTop: '16px' }}>
          Backend API: {typeof window !== 'undefined' && (window as any).NEXT_PUBLIC_API_BASE_URL
            ? (window as any).NEXT_PUBLIC_API_BASE_URL
            : 'http://localhost:8000'}
        </p>
      </div>
    </div>
  );
};

export default RAGChatbot;
