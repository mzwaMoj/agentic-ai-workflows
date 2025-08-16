import React, { useState } from 'react';
import './ChatInput.css';

const ChatInput = ({ onSendMessage, isLoading, suggestions = [], placeholder = "Type your query here..." }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleSuggestionClick = (suggestionText) => {
    if (!isLoading) {
      onSendMessage(suggestionText);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-container">      {/* Query Suggestions */}
      {suggestions.length > 0 && (
        <div className="suggestions-container">
          <div className="suggestions-grid">            {suggestions.slice(0, 6).map((suggestion, index) => (              <button
                key={index}
                className="suggestion-bubble"
                onClick={() => handleSuggestionClick(typeof suggestion === 'string' ? suggestion : suggestion.text)}
                disabled={isLoading}
              >
                {typeof suggestion === 'string' ? suggestion : suggestion.text}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Message Input */}
      <form onSubmit={handleSubmit} className="input-form">
        <div className="input-wrapper">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            className="message-input"
            rows="1"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!message.trim() || isLoading}
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInput;
