import React, { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import text2sqlService from '../../services/text2sqlService';
import logger from '../../services/logger';
import './ChatBot.css';

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiHealth, setApiHealth] = useState('unknown');
  const messagesEndRef = useRef(null);
  // Component lifecycle logging
  useEffect(() => {
    logger.componentMount('ChatBot', { 
      initialMessagesLength: messages.length,
      apiHealth,
      isLoading 
    });
    
    return () => {
      logger.componentUnmount('ChatBot');
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);
  // Check API health and load initial message
  useEffect(() => {
    const initializeChat = async () => {
      logger.info('Initializing ChatBot component');
      
      try {
        logger.debug('Starting API health check');
        await text2sqlService.getHealthStatus();
        setApiHealth('healthy');
        logger.success('API health check passed');
      } catch (err) {
        logger.error('API health check failed', err);
        setApiHealth('unhealthy');
        setError('Unable to connect to the API server. Please check your connection.');
      }

      // Add welcome message
      const welcomeMessage = {
        role: 'assistant',
        content: 'Hello! I\'m your Text2SQL AI Assistant. I can help you analyze data by converting your natural language questions into SQL queries and generating interactive charts. Try asking me something like "Show me customer balances by income category" or "What are the top performing products?"',
        timestamp: new Date().toISOString()
      };
      
      setMessages([welcomeMessage]);
      logger.info('ChatBot initialized successfully', { 
        apiHealth: apiHealth,
        welcomeMessageAdded: true 
      });
    };    initializeChat();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const handleSendMessage = async (messageText) => {
    if (!messageText.trim()) {
      logger.warn('Empty message submitted');
      return;
    }

    logger.userAction('Send Message', { 
      messageLength: messageText.length,
      messagePreview: messageText.substring(0, 100)
    });

    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };
    
    // Add user message immediately
    setMessages(prev => {
      const newMessages = [...prev, userMessage];
      logger.debug('User message added to chat', { 
        totalMessages: newMessages.length,
        userMessage: userMessage.content.substring(0, 100)
      });
      return newMessages;
    });
    
    setIsLoading(true);
    setError(null);
    logger.info('Starting message processing', { messageText: messageText.substring(0, 100) });

    try {
      // Prepare chat history for API
      const chatHistory = text2sqlService.formatChatHistory(messages);
      logger.debug('Chat history prepared', { historyLength: chatHistory.length });

      // Send to Text2SQL backend
      logger.info('Sending request to Text2SQL service');
      const response = await text2sqlService.generateSQL(messageText, {
        includeCharts: true,
        maxResults: 100,
        chatHistory: chatHistory
      });

      if (response.success) {
        logger.success('Text2SQL request completed successfully', {
          hasResponse: !!response.response,
          hasChart: !!response.chart_html,
          hasSql: !!response.sql_query,
          hasResults: !!(response.sql_results && response.sql_results.length > 0),
          resultCount: response.sql_results?.length || 0
        });

        // Add assistant response with embedded chart and results data
        const assistantMessage = {
          role: 'assistant',
          content: response.response || 'Query executed successfully.',
          timestamp: new Date().toISOString(),
          // Embed chart and results data directly in the message
          chartHtml: response.chart_html,
          sqlQuery: response.sql_query,
          sqlResults: response.sql_results,
          hasChart: !!response.chart_html,
          hasData: !!(response.sql_results && response.sql_results.length > 0)
        };

        setMessages(prev => {
          const newMessages = [...prev, assistantMessage];
          logger.info('Assistant response added to chat', {
            totalMessages: newMessages.length,
            responseLength: assistantMessage.content.length,
            hasChart: assistantMessage.hasChart,
            hasData: assistantMessage.hasData
          });
          return newMessages;
        });
      } else {
        logger.error('Text2SQL request failed', { 
          success: response.success, 
          error: response.error 
        });
        throw new Error(response.error || 'Query execution failed');
      }

    } catch (err) {
      logger.error('Error processing query', err);
      setError(err.message || 'Failed to process your request. Please try again.');
      
      // Add error message
      const errorMessage = {
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${err.message}. Please try rephrasing your question or check if you're asking about data that exists in our database.`,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => {
        const newMessages = [...prev, errorMessage];
        logger.warn('Error message added to chat', {
          totalMessages: newMessages.length,
          errorMessage: err.message
        });
        return newMessages;
      });
    } finally {
      setIsLoading(false);
      logger.debug('Message processing completed');
    }
  };

  const clearConversation = () => {
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m your Text2SQL AI Assistant. I can help you analyze data by converting your natural language questions into SQL queries and generating interactive charts. What would you like to explore?',
        timestamp: new Date().toISOString()
      }
    ]);
    setError(null);
  };
  const getSampleQueries = () => [
    { text: "Show me customer balances by income category" },
    { text: "What are the average account balances for each customer type?" },
    { text: "List customers with balances over $10,000" },
    { text: "Show transaction trends over time" },
    { text: "Which customers have the highest balances?" }
  ];
  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <div className="header-content">
          <h2>Text2SQL AI Assistant</h2>
          <div className="api-status">
            <span className={`status-indicator ${apiHealth}`}>
              {apiHealth === 'healthy' ? '🟢' : apiHealth === 'unhealthy' ? '🔴' : '🟡'} 
              {apiHealth === 'healthy' ? 'Connected' : apiHealth === 'unhealthy' ? 'Disconnected' : 'Checking...'}
            </span>
          </div>
        </div>
        <button onClick={clearConversation} className="clear-button">
          🗑️ Clear Chat
        </button>
      </div>

      <div className="chat-messages">        {messages.map((message, index) => (
          <ChatMessage
            key={index}
            message={message}
            isUser={message.role === 'user'}
          />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            {error}
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        suggestions={messages.length <= 1 ? getSampleQueries() : []}
        placeholder="Ask me to analyze your data... (e.g., 'Show customer balances by region')"
      />
    </div>
  );
};

export default ChatBot;
