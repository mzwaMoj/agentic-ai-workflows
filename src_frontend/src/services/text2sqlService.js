/**
 * Text2SQL API Service
 * Handles communication with the Text2SQL FastAPI backend
 */

import logger from './logger';
import performanceMonitor from './performanceMonitor';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class Text2SqlService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = 120000; // 2 minutes timeout for complex queries
  }
  /**
   * Generate SQL from natural language query with chart support
   * @param {string} query - Natural language query
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Response with SQL, results, and charts
   */
  async generateSQL(query, options = {}) {
    logger.info('Starting SQL generation', { 
      queryLength: query?.length || 0, 
      queryPreview: query?.substring(0, 100),
      options 
    });
    
    const payload = {
      query,
      include_charts: options.includeCharts ?? true,
      max_results: options.maxResults ?? 100,
      chat_history: options.chatHistory ?? []
    };    try {
      const startTime = Date.now();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => {
        controller.abort();
        logger.warn('Request timeout triggered', { duration: this.timeout });
      }, this.timeout);

      logger.apiCall('POST', `${this.baseURL}/api/v1/text2sql/generate`, payload);

      const response = await fetch(`${this.baseURL}/api/v1/text2sql/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      const duration = Date.now() - startTime;

      // Monitor API performance
      performanceMonitor.monitorApiCall(
        `${this.baseURL}/api/v1/text2sql/generate`,
        'POST',
        duration,
        response.status
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        logger.apiResponse('POST', `${this.baseURL}/api/v1/text2sql/generate`, response.status, errorData, duration);
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }      const result = await response.json();
      logger.apiResponse('POST', `${this.baseURL}/api/v1/text2sql/generate`, response.status, {
        success: result.success,
        hasSql: !!result.sql_query,
        hasResults: !!result.sql_results,
        hasCharts: !!result.chart_html,
        resultCount: result.sql_results?.length || 0
      }, duration);
      
      // Validate response structure
      if (!result.hasOwnProperty('success')) {
        logger.error('Invalid response format from server', { result });
        throw new Error('Invalid response format from server');
      }

      logger.success('SQL generation completed successfully', {
        duration,
        success: result.success,
        sqlGenerated: !!result.sql_query,
        resultsReturned: result.sql_results?.length || 0
      });

      return result;
    } catch (error) {
      logger.error('Text2SQL generation failed', error);
      throw this.handleError(error);
    }
  }
  /**
   * Validate a SQL query
   * @param {string} query - SQL query to validate
   * @returns {Promise<Object>} Validation result
   */
  async validateQuery(query) {
    logger.debug('Starting query validation', { queryLength: query?.length, queryPreview: query?.substring(0, 100) });
    
    try {
      const startTime = Date.now();
      logger.apiCall('POST', `${this.baseURL}/api/v1/text2sql/validate`, { query });
      
      const response = await fetch(`${this.baseURL}/api/v1/text2sql/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query })
      });

      const duration = Date.now() - startTime;

      if (!response.ok) {
        logger.apiResponse('POST', `${this.baseURL}/api/v1/text2sql/validate`, response.status, null, duration);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      logger.apiResponse('POST', `${this.baseURL}/api/v1/text2sql/validate`, response.status, result, duration);
      logger.success('Query validation completed', { duration, isValid: result.valid });
      
      return result;
    } catch (error) {
      logger.error('Query validation failed', error);
      throw this.handleError(error);
    }
  }
  /**
   * Get available table information
   * @returns {Promise<Object>} Table schema information
   */
  async getTableInfo() {
    logger.debug('Fetching table information');
    
    try {
      const startTime = Date.now();
      logger.apiCall('GET', `${this.baseURL}/api/v1/text2sql/tables`);
      
      const response = await fetch(`${this.baseURL}/api/v1/text2sql/tables`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const duration = Date.now() - startTime;

      if (!response.ok) {
        logger.apiResponse('GET', `${this.baseURL}/api/v1/text2sql/tables`, response.status, null, duration);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      logger.apiResponse('GET', `${this.baseURL}/api/v1/text2sql/tables`, response.status, {
        tableCount: result.tables?.length || 0
      }, duration);
      logger.success('Table information fetched successfully', { 
        duration, 
        tableCount: result.tables?.length || 0 
      });

      return result;
    } catch (error) {
      logger.error('Failed to fetch table info', error);
      throw this.handleError(error);
    }
  }
  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  async getHealthStatus() {
    logger.debug('Checking API health status');
    
    try {
      const startTime = Date.now();
      logger.apiCall('GET', `${this.baseURL}/api/v1/health`);
      
      const response = await fetch(`${this.baseURL}/api/v1/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const duration = Date.now() - startTime;

      if (!response.ok) {
        logger.apiResponse('GET', `${this.baseURL}/api/v1/health`, response.status, null, duration);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      logger.apiResponse('GET', `${this.baseURL}/api/v1/health`, response.status, result, duration);
      logger.success('Health check completed successfully', { duration, status: result.status });

      return result;
    } catch (error) {
      logger.error('Health check failed', error);
      throw this.handleError(error);
    }
  }

  /**
   * Handle and categorize errors
   * @param {Error} error - Original error
   * @returns {Error} Processed error with user-friendly message
   */
  handleError(error) {
    if (error.name === 'AbortError') {
      return new Error('Query timeout - please try a simpler request or check your connection');
    }
    
    if (error.message.includes('500')) {
      return new Error('Server error - please try again later');
    }
    
    if (error.message.includes('422')) {
      return new Error('Invalid request - please check your query format');
    }
    
    if (error.message.includes('503')) {
      return new Error('Service temporarily unavailable - please try again in a moment');
    }
    
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      return new Error('Network error - please check your connection and try again');
    }
    
    return error;
  }

  /**
   * Format chat history for API consumption
   * @param {Array} messages - Chat messages
   * @returns {Array} Formatted chat history
   */
  formatChatHistory(messages) {
    return messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
  }
}

// Create and export singleton instance
const text2sqlService = new Text2SqlService();
export default text2sqlService;
