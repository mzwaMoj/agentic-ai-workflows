// Frontend Logger Service
class Logger {
  constructor() {
    this.logLevel = process.env.NODE_ENV === 'production' ? 'warn' : 'debug';
    this.logs = [];
    this.maxLogs = 1000; // Keep last 1000 logs in memory
    
    // Initialize console styling
    this.styles = {
      error: 'color: #ff4444; font-weight: bold;',
      warn: 'color: #ffaa00; font-weight: bold;',
      info: 'color: #4444ff; font-weight: bold;',
      debug: 'color: #666666;',
      success: 'color: #44ff44; font-weight: bold;'
    };
  }

  formatMessage(level, message, data = null) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      data,
      url: window.location.href,
      userAgent: navigator.userAgent.substring(0, 100)
    };
    
    // Add to memory logs
    this.logs.push(logEntry);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift(); // Remove oldest log
    }
    
    return logEntry;
  }

  shouldLog(level) {
    const levels = { debug: 0, info: 1, warn: 2, error: 3 };
    return levels[level] >= levels[this.logLevel];
  }

  debug(message, data = null) {
    if (!this.shouldLog('debug')) return;
    
    const logEntry = this.formatMessage('debug', message, data);
    console.log(`%c[DEBUG] ${logEntry.timestamp} - ${message}`, this.styles.debug, data || '');
    this.sendToServer(logEntry);
  }

  info(message, data = null) {
    if (!this.shouldLog('info')) return;
    
    const logEntry = this.formatMessage('info', message, data);
    console.log(`%c[INFO] ${logEntry.timestamp} - ${message}`, this.styles.info, data || '');
    this.sendToServer(logEntry);
  }

  warn(message, data = null) {
    if (!this.shouldLog('warn')) return;
    
    const logEntry = this.formatMessage('warn', message, data);
    console.warn(`%c[WARN] ${logEntry.timestamp} - ${message}`, this.styles.warn, data || '');
    this.sendToServer(logEntry);
  }

  error(message, error = null) {
    const logEntry = this.formatMessage('error', message, {
      error: error ? {
        message: error.message,
        stack: error.stack,
        name: error.name
      } : null
    });
    
    console.error(`%c[ERROR] ${logEntry.timestamp} - ${message}`, this.styles.error, error);
    this.sendToServer(logEntry);
  }

  success(message, data = null) {
    const logEntry = this.formatMessage('success', message, data);
    console.log(`%c[SUCCESS] ${logEntry.timestamp} - ${message}`, this.styles.success, data || '');
    this.sendToServer(logEntry);
  }

  // Log API calls
  apiCall(method, url, requestData = null) {
    this.debug(`API Call: ${method} ${url}`, {
      method,
      url,
      requestData: requestData ? JSON.stringify(requestData).substring(0, 500) : null
    });
  }

  apiResponse(method, url, status, responseData = null, duration = null) {
    const level = status >= 400 ? 'error' : status >= 300 ? 'warn' : 'success';
    this[level](`API Response: ${method} ${url} - ${status}${duration ? ` (${duration}ms)` : ''}`, {
      method,
      url,
      status,
      duration,
      responseData: responseData ? JSON.stringify(responseData).substring(0, 500) : null
    });
  }

  // Log component lifecycle
  componentMount(componentName, props = null) {
    this.debug(`Component Mounted: ${componentName}`, { componentName, props });
  }

  componentUnmount(componentName) {
    this.debug(`Component Unmounted: ${componentName}`, { componentName });
  }

  componentError(componentName, error) {
    this.error(`Component Error in ${componentName}`, error);
  }

  // Log user interactions
  userAction(action, details = null) {
    this.info(`User Action: ${action}`, { action, details });
  }
  // Send logs to server (optional)
  async sendToServer(logEntry) {
    // Only send error and warn logs to server to avoid spam
    if (logEntry.level !== 'error' && logEntry.level !== 'warn') {
      return;
    }

    try {
      // Check if we have a valid API URL and logging is enabled
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const loggingEnabled = process.env.REACT_APP_ENABLE_SERVER_LOGGING === 'true';
      
      if (!loggingEnabled) {
        return; // Server logging disabled
      }

      // Don't await this to avoid blocking the main thread
      fetch(`${apiUrl}/api/v1/frontend-logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logEntry)
      }).catch(() => {
        // Silently fail if logging endpoint is not available
        // This prevents the 404 errors in the console
      });
    } catch (error) {
      // Don't log this error to avoid infinite loops
    }
  }

  // Get all logs for debugging
  getAllLogs() {
    return this.logs;
  }

  // Download logs as file
  downloadLogs() {
    const logsText = this.logs.map(log => 
      `${log.timestamp} [${log.level.toUpperCase()}] ${log.message} ${log.data ? JSON.stringify(log.data) : ''}`
    ).join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `frontend-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Clear logs
  clearLogs() {
    this.logs = [];
    console.clear();
    this.info('Logs cleared');
  }
}

// Create singleton instance
const logger = new Logger();

// Add global error handlers
window.addEventListener('error', (event) => {
  logger.error('Global Error', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    stack: event.error?.stack
  });
});

window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled Promise Rejection', {
    reason: event.reason,
    stack: event.reason?.stack
  });
});

// Add to window for debugging
window.logger = logger;

// Add console helper message
if (typeof window !== 'undefined') {
  console.log(
    '%c🚀 Text2SQL Debug Tools Available!',
    'color: #4CAF50; font-size: 16px; font-weight: bold;'
  );
  console.log(
    '%cUse these commands in the console:',
    'color: #2196F3; font-size: 14px; font-weight: bold;'
  );
  console.log('%c• window.debugApp.showLogs() - Open log viewer', 'color: #666;');
  console.log('%c• window.debugApp.getLogs() - Get all logs', 'color: #666;');
  console.log('%c• window.debugApp.clearLogs() - Clear logs', 'color: #666;');
  console.log('%c• window.debugApp.downloadLogs() - Download logs', 'color: #666;');
  console.log('%c• Ctrl+Shift+L - Toggle log viewer', 'color: #666;');
  console.log('%c• window.logger - Direct access to logger', 'color: #666;');
  console.log(
    '%c─────────────────────────────────────────────',
    'color: #ddd;'
  );
}

export default logger;
