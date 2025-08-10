/**
 * Chat API Service
 * Handles communication with the chatbot backend API
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ChatService {
  /**
   * Send a message to the chatbot and get a response
   * @param {string} message - User's message
   * @param {Array} chatHistory - Previous conversation history
   * @returns {Promise<Object>} Chat response with updated history
   */
  async sendMessage(message, chatHistory = []) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          chat_history: chatHistory
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw new Error(`Failed to send message: ${error.message}`);
    }
  }

  /**
   * Get suggested queries for user guidance
   * @returns {Promise<Array>} Array of query suggestions
   */
  async getSuggestions() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/suggestions`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.suggestions;
    } catch (error) {
      console.error('Error getting suggestions:', error);
      throw new Error(`Failed to get suggestions: ${error.message}`);
    }
  }

  /**
   * Check if the API is available
   * @returns {Promise<boolean>} True if API is available
   */
  async isAvailable() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      return response.ok;
    } catch (error) {
      console.error('API not available:', error);
      return false;
    }
  }
}

// Create and export a singleton instance
const chatService = new ChatService();
export default chatService;
