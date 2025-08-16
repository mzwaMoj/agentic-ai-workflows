import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import text2sqlService from '../../services/text2sqlService';
import logger from '../../services/logger';
import './ChatBot.css';

const ChatBot = () => {  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello...! How can I help you today?',
      timestamp: new Date().toISOString()
    }
  ]);const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiHealth, setApiHealth] = useState('unknown');
  const [showSuggestions, setShowSuggestions] = useState(true); // Hide after first message
  const messagesEndRef = useRef(null);

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  // Scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const checkApiHealth = async () => {
    try {
      const healthStatus = await text2sqlService.getHealthStatus();
      setApiHealth(healthStatus.status === 'healthy' ? 'healthy' : 'unhealthy');
    } catch (error) {
      setApiHealth('unhealthy');
      logger.error('API health check failed', error);
    }
  };
  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    // Hide suggestions after first user message
    setShowSuggestions(false);

    // Add user message
    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      logger.info('Sending message to text2sql service', { message: messageText });
      
      // Get chat history for context (last 10 messages)
      const chatHistory = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await text2sqlService.generateSQL(messageText, {
        includeCharts: true,
        maxResults: 100,
        chatHistory: chatHistory
      });

      logger.info('Received response from text2sql service', { success: response.success });      if (response.success) {
        // Extract actual data from sql_results array
        let extractedData = null;
        let sqlQuery = response.sql_query;
        
        if (response.sql_results && response.sql_results.length > 0) {
          // The backend returns sql_results as an array of result objects
          // Each object has {type, query_info, data, user_request}
          const successResult = response.sql_results.find(result => result.type === 'sql_success');
          if (successResult && successResult.data && Array.isArray(successResult.data)) {
            extractedData = successResult.data;
          }
          
          // Use query_info as sql_query if not provided directly
          if (!sqlQuery && successResult && successResult.query_info) {
            sqlQuery = successResult.query_info;
          }
        }

        // Create assistant message with rich content
        const assistantMessage = {
          role: 'assistant',
          content: response.response || 'I\'ve processed your request.',
          timestamp: new Date().toISOString(),
          hasChart: !!response.chart_html,
          chartHtml: response.chart_html,
          hasData: !!(extractedData && extractedData.length > 0),
          sqlResults: extractedData,
          sqlQuery: sqlQuery,
          executionTime: response.execution_time
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Handle error response
        const errorMessage = {
          role: 'assistant',
          content: `I encountered an error: ${response.error || 'Something went wrong'}`,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, errorMessage]);
        setError(response.error || 'Unknown error occurred');
      }
    } catch (error) {
      logger.error('Failed to process message', error);
      
      const errorMessage = {
        role: 'assistant',
        content: `I'm sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };  const handleClearChat = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m your AI Data Analyst Assistant. I can help you analyze your data by converting natural language questions into SQL queries and creating interactive visualizations. Try one of the suggestions below or ask me anything about your data!',
        timestamp: new Date().toISOString()
      }
    ]);
    setError(null);
    setShowSuggestions(true); // Show suggestions again when chat is cleared
  };
  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <div className="header-content">
          <h2>AI Data Analyst</h2>
          <div className="api-status">
            <span className={`status-indicator ${apiHealth}`}>
              {apiHealth === 'healthy' ? '🟢' : apiHealth === 'unhealthy' ? '🔴' : '🟡'} 
              {apiHealth === 'healthy' ? 'Connected' : apiHealth === 'unhealthy' ? 'Disconnected' : 'Checking...'}
            </span>
          </div>
        </div>
        <button className="clear-button" onClick={handleClearChat}>
          🗑️ Clear Chat
        </button>
      </div>
      
      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}
      
      <div className="chat-messages">
        {messages.map((message, index) => (
          <ChatMessage
            key={index}
            message={message}
            isUser={message.role === 'user'}
          />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>
        <div className="chat-input-container">
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          suggestions={showSuggestions ? [
            "show me customer base chart by account type and age group",
            "Show me a charts for transaction volume and amount over time",
            "Display account balances by customer type",
            "Show me the top 10 customers by balance",
            "Which customers have the most products with us?",
            "What's our total customer deposit base by account type"
          ] : []}
          placeholder="Ask me about your data... (e.g., 'Show me a pie chart of transaction volume by channel')"
        />
      </div>
    </div>
  );
};

export default ChatBot;
