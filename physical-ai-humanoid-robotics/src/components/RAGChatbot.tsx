import React, { useState, useRef, useEffect } from 'react';
import './RAGChatbot.css';

/**
 * RAG Chatbot Component
 * A floating chatbot widget integrated into the Docusaurus documentation site
 */
const RAGChatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Configuration for the backend API
  const API_BASE_URL = typeof window !== 'undefined' 
    ? (process.env.NEXT_PUBLIC_API_BASE_URL || process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000')
    : 'http://localhost:8000';

  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const closeChat = () => {
    setIsOpen(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputValue(e.target.value);
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    // Save the message before clearing input
    const messageText = inputValue;
    
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const requestBody: any = {
        message: messageText,
        top_k: 5
      };

      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      console.log('Sending request to:', `${API_BASE_URL}/chat`);
      console.log('Request body:', requestBody);

      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log('Response data:', data);

      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date(),
        sources: data.sources || [],
        context_used: data.context_used || []
      };

      setMessages(prevMessages => [...prevMessages, botMessage]);
    } catch (err: any) {
      console.error('Error sending message:', err);
      setError(`Failed to get response: ${err.message}`);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

      const errorMessage = {
        id: Date.now() + 1,
        text: `Sorry, I encountered an error: ${err.message}. Please try again.`,
        sender: 'bot',
        timestamp: new Date(),
        isError: true
      };

      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatSources = (sources: any[]) => {
    if (!sources || sources.length === 0) return null;

    // Filter out Unknown sources
    const validSources = sources.filter(source => 
      source.relative_path && source.relative_path !== 'Unknown'
    );

    if (validSources.length === 0) return null;

    return (
      <div className="sources-section">
        <h4>Sources:</h4>
        <ul className="sources-list">
          {validSources.map((source, index) => (
            <li key={index} className="source-item">
              <div className="source-path">{source.relative_path}</div>
              <div className="source-score">Relevance: {(source.score * 100).toFixed(1)}%</div>
              <div className="source-preview">{source.content_preview}</div>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  const clearConversation = () => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  };

  return (
    <>
      {/* Floating chat button */}
      {!isOpen && (
        <button className="chatbot-float-button" onClick={toggleChat} aria-label="Open chat">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 13.54 2.36 15.02 3.02 16.35L2 22L7.65 20.98C8.98 21.64 10.46 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM8 14.5C7.17 14.5 6.5 13.83 6.5 13C6.5 12.17 7.17 11.5 8 11.5C8.83 11.5 9.5 12.17 9.5 13C9.5 13.83 8.83 14.5 8 14.5ZM12 14.5C11.17 14.5 10.5 13.83 10.5 13C10.5 12.17 11.17 11.5 12 11.5C12.83 11.5 13.5 12.17 13.5 13C13.5 13.83 12.83 14.5 12 14.5ZM16 14.5C15.17 14.5 14.5 13.83 14.5 13C14.5 12.17 15.17 11.5 16 11.5C16.83 11.5 17.5 12.17 17.5 13C17.5 13.83 16.83 14.5 16 14.5Z" fill="white"/>
          </svg>
        </button>
      )}

      {/* Chat window */}
      {isOpen && (
        <div className="chatbot-container">
          <div className="chatbot-header">
            <div className="chatbot-header-content">
              <div className="chatbot-header-left">
                <h3>Physical AI & Humanoid Robotics Assistant</h3>
                {sessionId && (
                  <span className="session-indicator" title={`Session ID: ${sessionId}`}>
                    Session: {sessionId.substring(0, 8)}...
                  </span>
                )}
              </div>
              <div className="chatbot-header-actions">
                <button
                  className="chatbot-clear-button"
                  onClick={clearConversation}
                  aria-label="Clear conversation"
                  title="Clear conversation history"
                >
                  Clear
                </button>
                <button className="chatbot-close-button" onClick={closeChat} aria-label="Close chat">
                  ×
                </button>
              </div>
            </div>
          </div>

          <div className="chatbot-messages">
            {messages.length === 0 ? (
              <div className="chatbot-welcome">
                <p>Hello! I'm your Physical AI & Humanoid Robotics documentation assistant.</p>
                <p>Ask me anything about the documentation, and I'll provide relevant answers with sources.</p>
                <p className="welcome-note">Your conversation is preserved during this session.</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`chatbot-message ${message.sender}-message`}
                >
                  <div className="message-content">
                    <div className="message-text">{message.text}</div>
                    {message.sender === 'bot' && message.sources && formatSources(message.sources)}
                  </div>
                  <div className="message-timestamp">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="chatbot-message bot-message">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {error && (
            <div className="chatbot-error">
              {error}
            </div>
          )}

          <div className="chatbot-input-area">
            <textarea
              value={inputValue}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about Physical AI & Humanoid Robotics..."
              className="chatbot-input"
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="chatbot-send-button"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default RAGChatbot;
