import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import io from 'socket.io-client';

const API_SERVER = 'http://localhost:8002/api/chat';

const ChatPanel = ({ currentFolder, selectedFiles, showFiles }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const socketRef = useRef(null);

  // Initialize connection to chat server
  useEffect(() => {
    const connectToChatServer = async () => {
      try {
        // First, establish connection to get session
        const response = await fetch(`${API_SERVER}/init`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            currentFolder,
            selectedFiles
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          setSessionId(data.sessionId);
          setIsConnected(true);
          
          // Add welcome message
          setMessages([{
            id: 'welcome',
            content: 'Welcome to LabAcc Copilot! I can help you analyze experimental data, organize files, and suggest optimizations.',
            author: 'Assistant',
            createdAt: new Date().toISOString(),
            type: 'ai_message'
          }]);
        }
      } catch (error) {
        console.error('Failed to connect to chat server:', error);
        setIsConnected(false);
        
        // Add offline message
        setMessages([{
          id: 'offline',
          content: 'Chat is currently offline. The FastAPI server may not be running on port 8002. Please check the backend server.',
          author: 'System',
          createdAt: new Date().toISOString(),
          type: 'system_message'
        }]);
      }
    };

    connectToChatServer();

    // Cleanup on unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, []);

  // Update context when folder or files change
  useEffect(() => {
    if (sessionId) {
      // Send context update to server
      fetch(`${API_SERVER}/context`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          currentFolder,
          selectedFiles
        })
      }).catch(console.error);
    }
  }, [currentFolder, selectedFiles, sessionId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (messageContent) => {
    if (!isConnected || isLoading) return;

    const userMessage = {
      id: Date.now(),
      content: messageContent,
      author: 'User',
      createdAt: new Date().toISOString(),
      type: 'user_message'
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_SERVER}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          message: messageContent,
          currentFolder,
          selectedFiles
        })
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage = {
          id: Date.now() + 1,
          content: data.response || 'I received your message but had trouble processing it.',
          author: data.author || 'Assistant',
          createdAt: new Date().toISOString(),
          type: 'ai_message'
        };
        
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        author: 'System',
        createdAt: new Date().toISOString(),
        type: 'error_message'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !isConnected || isLoading) return;
    
    const messageContent = inputValue.trim();
    setInputValue('');
    
    await sendMessage(messageContent);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const renderMessage = (message) => {
    const isUser = message.author === 'User' || message.type === 'user_message';
    const isSystem = message.type === 'system_message' || message.type === 'error_message';
    
    return (
      <div
        key={message.id}
        className={`message ${isUser ? 'user-message' : isSystem ? 'system-message' : 'ai-message'}`}
      >
        <div className="message-header">
          <span className="message-author">
            {isUser ? 'You' : (message.author || 'Assistant')}
          </span>
          <span className="message-time">
            {new Date(message.createdAt).toLocaleTimeString()}
          </span>
        </div>
        <div className="message-content">
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    );
  };

  return (
    <div className={`chat-panel ${!showFiles ? 'full-width' : ''}`}>
      <div className="chat-header">
        <h3>AI Assistant</h3>
        <div className="connection-status">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`} />
          {isConnected ? 'Connected' : 'Connecting...'}
        </div>
      </div>
      
      {currentFolder && (
        <div className="chat-context">
          <span className="context-label">📁 Current folder:</span>
          <span className="context-value">{currentFolder}</span>
        </div>
      )}
      
      {selectedFiles && selectedFiles.length > 0 && (
        <div className="chat-context">
          <span className="context-label">📎 Selected files:</span>
          <span className="context-value">{selectedFiles.length} files</span>
        </div>
      )}
      
      <div className="chat-messages">
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="message ai-message loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={
            isConnected 
              ? "Ask me about your experiments, data analysis, or file organization..." 
              : "Chat unavailable - Chainlit server not running"
          }
          disabled={!isConnected || isLoading}
          rows={2}
        />
        <button
          className="chat-send-button"
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || !isConnected || isLoading}
        >
          {isLoading ? '...' : '➤'}
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;