import React, { useState, useRef, useEffect } from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

const RAGChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backendUrl, setBackendUrl] = useState('');
  const messagesEndRef = useRef(null);

  // Determine backend URL based on environment
  useEffect(() => {
    // In production, you might use a different URL
    // For now, assuming the backend runs on port 8000
    const isDevelopment = typeof process !== 'undefined' && process.env && process.env.NODE_ENV === 'development';
    const url = isDevelopment
      ? 'http://localhost:8000'
      : 'https://your-backend-url.onrender.com'; // Replace with your deployed backend URL

    setBackendUrl(url);
  }, []);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Make component available globally when mounted
  useEffect(() => {
    window.RAGChatbotComponent = {
      open: () => setIsOpen(true),
      close: () => setIsOpen(false),
      toggle: () => setIsOpen(prev => !prev),
      sendMessage: (message) => {
        setInputValue(message);
        // Small delay to ensure state is updated
        setTimeout(() => {
          document.dispatchEvent(new CustomEvent('ragChatbotSendMessage', { detail: { message } }));
        }, 0);
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputValue, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${backendUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          top_k: 3
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        contextUsed: data.context_used
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Listen for external send message events
  useEffect(() => {
    const handleExternalSendMessage = (e) => {
      if (e.detail && e.detail.message) {
        setInputValue(e.detail.message);
        // Small delay to ensure state is updated
        setTimeout(() => {
          sendMessage();
        }, 0);
      }
    };

    document.addEventListener('ragChatbotSendMessage', handleExternalSendMessage);
    return () => {
      document.removeEventListener('ragChatbotSendMessage', handleExternalSendMessage);
    };
  }, [inputValue, isLoading, backendUrl]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const welcomeMessage = "Hello! I'm your RAG-enhanced chatbot. I can answer questions about the documentation using the content from this site. How can I help you today?";

  return (
    <BrowserOnly>
      {() => (
        <div className="rag-chatbot">
          {/* Chatbot Widget Button */}
          {!isOpen && (
            <button
              className="chatbot-button"
              onClick={toggleChat}
              style={{
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                backgroundColor: '#007cba',
                color: 'white',
                border: 'none',
                fontSize: '24px',
                cursor: 'pointer',
                zIndex: 1000,
                boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              💬
            </button>
          )}

          {/* Chat Window */}
          {isOpen && (
            <div
              className="chat-window"
              style={{
                position: 'fixed',
                bottom: '20px',
                right: '20px',
                width: '350px',
                height: '500px',
                backgroundColor: 'white',
                borderRadius: '10px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                display: 'flex',
                flexDirection: 'column',
                zIndex: 1000,
                fontFamily: 'Arial, sans-serif',
                border: '1px solid #ddd'
              }}
            >
              {/* Header */}
              <div
                className="chat-header"
                style={{
                  backgroundColor: '#007cba',
                  color: 'white',
                  padding: '15px',
                  borderTopLeftRadius: '10px',
                  borderTopRightRadius: '10px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}
              >
                <h3 style={{ margin: 0, fontSize: '16px' }}>Documentation Assistant</h3>
                <button
                  onClick={toggleChat}
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'white',
                    fontSize: '18px',
                    cursor: 'pointer'
                  }}
                >
                  ×
                </button>
              </div>

              {/* Messages Container */}
              <div
                className="chat-messages"
                style={{
                  flex: 1,
                  padding: '15px',
                  overflowY: 'auto',
                  backgroundColor: '#f9f9f9'
                }}
              >
                {messages.length === 0 && (
                  <div className="welcome-message" style={{ marginBottom: '10px', fontStyle: 'italic', color: '#666' }}>
                    {welcomeMessage}
                  </div>
                )}

                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`message ${msg.role}`}
                    style={{
                      marginBottom: '10px',
                      textAlign: msg.role === 'user' ? 'right' : 'left'
                    }}
                  >
                    <div
                      style={{
                        display: 'inline-block',
                        padding: '8px 12px',
                        borderRadius: '18px',
                        backgroundColor: msg.role === 'user' ? '#007cba' : '#e5e5ea',
                        color: msg.role === 'user' ? 'white' : 'black',
                        maxWidth: '80%'
                      }}
                    >
                      {msg.content}

                      {msg.contextUsed && msg.contextUsed.length > 0 && (
                        <details style={{ marginTop: '5px', fontSize: '0.8em', color: '#666' }}>
                          <summary>Context Used</summary>
                          <ul style={{ paddingLeft: '15px', margin: '5px 0' }}>
                            {msg.contextUsed.map((ctx, idx) => (
                              <li key={idx}>{ctx.content.substring(0, 100)}{ctx.content.length > 100 ? '...' : ''}</li>
                            ))}
                          </ul>
                        </details>
                      )}
                    </div>
                  </div>
                ))}

                {isLoading && (
                  <div className="loading-message" style={{ marginBottom: '10px', textAlign: 'left' }}>
                    <div style={{ display: 'inline-block', padding: '8px 12px', borderRadius: '18px', backgroundColor: '#e5e5ea', color: 'black' }}>
                      Thinking...
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div
                className="chat-input-area"
                style={{
                  padding: '10px',
                  borderTop: '1px solid #eee',
                  backgroundColor: 'white'
                }}
              >
                <div style={{ display: 'flex' }}>
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question..."
                    rows={2}
                    style={{
                      flex: 1,
                      padding: '10px',
                      borderRadius: '18px',
                      border: '1px solid #ddd',
                      resize: 'none',
                      marginRight: '8px'
                    }}
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputValue.trim() || isLoading}
                    style={{
                      padding: '10px 15px',
                      borderRadius: '18px',
                      backgroundColor: inputValue.trim() && !isLoading ? '#007cba' : '#ccc',
                      color: 'white',
                      border: 'none',
                      cursor: inputValue.trim() && !isLoading ? 'pointer' : 'not-allowed'
                    }}
                  >
                    Send
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </BrowserOnly>
  );
};

export default RAGChatbot;