# Frontend Logging & Debugging System

This document describes the comprehensive logging and debugging system implemented in the Text2SQL frontend application.

## Overview

The logging system provides:
- **Background logging** for debugging and monitoring
- **Performance monitoring** for API calls and component renders
- **Hidden debug panel** accessible via keyboard shortcut
- **Console utilities** for developers
- **Automatic error tracking** and metrics collection

## Quick Start

### Console Commands
Open browser console and use these commands:

```javascript
// View all logs
window.debugApp.getLogs()

// Open visual log viewer
window.debugApp.showLogs()

// Clear all logs
window.debugApp.clearLogs()

// Download logs as file
window.debugApp.downloadLogs()

// Get performance metrics
window.debugApp.getPerformance()

// Start timing an operation
const timer = window.debugApp.startTiming('my-operation')
// ... do something ...
timer.end()
```

### Keyboard Shortcuts
- **Ctrl+Shift+L** - Toggle log viewer panel

## Logging Levels

### 1. Debug (Gray)
```javascript
logger.debug('Detailed information for debugging', { data: 'example' });
```
- Used for detailed debugging information
- Only shown in development mode
- Helpful for tracking application flow

### 2. Info (Blue)
```javascript
logger.info('General information', { userId: 123 });
```
- General application information
- User actions and significant events
- Always visible

### 3. Success (Green)
```javascript
logger.success('Operation completed successfully', { duration: 150 });
```
- Successful operations
- API calls that completed successfully
- Positive user feedback

### 4. Warning (Orange)
```javascript
logger.warn('Something needs attention', { issue: 'slow response' });
```
- Potential issues that don't break functionality
- Performance warnings
- Recoverable errors

### 5. Error (Red)
```javascript
logger.error('Something went wrong', error);
```
- Actual errors and exceptions
- Failed API calls
- Critical issues that affect functionality

## Specialized Logging

### API Calls
Automatically logged by the text2sqlService:
```javascript
// Automatically logs request
logger.apiCall('POST', '/api/v1/text2sql', requestData);

// Automatically logs response
logger.apiResponse('POST', '/api/v1/text2sql', 200, responseData, 150);
```

### Component Lifecycle
```javascript
// Component mounting
logger.componentMount('ChatBot', { props: componentProps });

// Component unmounting
logger.componentUnmount('ChatBot');

// Component errors
logger.componentError('ChatBot', error);
```

### User Actions
```javascript
logger.userAction('Send Message', { 
  messageLength: message.length,
  timestamp: new Date().toISOString()
});
```

## Performance Monitoring

### Automatic Monitoring
The system automatically tracks:
- **Page load metrics** (DOM content loaded, first paint, etc.)
- **API call performance** (duration, success rate, slow calls)
- **Memory usage** (heap size, usage percentage)
- **Long tasks** (JavaScript operations > 50ms)
- **Network connectivity** (online/offline status)

### Manual Performance Tracking
```javascript
// Time an operation
const timer = performanceMonitor.startTiming('data-processing');
// ... do work ...
const duration = timer.end(); // Returns duration in ms

// Monitor component render time
performanceMonitor.monitorComponentRender('MyComponent', renderTime);

// Record custom metrics
performanceMonitor.recordMetric('custom-metric', { value: 123 });
```

## Log Viewer Panel

### Opening the Panel
1. **Keyboard**: Press `Ctrl+Shift+L`
2. **Console**: Run `window.debugApp.showLogs()`

### Features
- **Real-time updates** - Logs appear as they happen
- **Filtering** - Filter by log level (error, warn, info, etc.)
- **Auto-refresh** - Toggle automatic refresh
- **Download** - Export logs as text file
- **Clear** - Remove all logs from memory

## Development vs Production

### Development Mode
- All log levels are shown
- Console shows colorful, formatted logs
- Debug panel keyboard shortcut is visible
- Performance monitoring is more verbose
- Memory usage is tracked every 30 seconds

### Production Mode
- Only warn and error logs are sent to server
- Debug and info logs are console-only
- Performance monitoring is less frequent
- Log viewer is still accessible but hidden

## Configuration

### Environment Variables
```bash
# Set log level (debug, info, warn, error)
REACT_APP_LOG_LEVEL=debug

# API endpoint for sending logs to server
REACT_APP_LOG_ENDPOINT=/api/v1/frontend-logs

# Enable/disable performance monitoring
REACT_APP_PERFORMANCE_MONITORING=true
```

### Logger Configuration
In `src/services/logger.js`:
```javascript
const logger = new Logger();
logger.logLevel = 'debug'; // Set minimum log level
logger.maxLogs = 1000;     // Maximum logs in memory
```

## Best Practices

### 1. Use Appropriate Log Levels
- `debug` - Temporary debugging information
- `info` - Important but normal events
- `success` - Confirmed successful operations
- `warn` - Unexpected but recoverable issues
- `error` - Actual failures and exceptions

### 2. Include Contextual Data
```javascript
// Good - includes context
logger.info('User message sent', { 
  messageLength: message.length,
  userId: user.id,
  timestamp: new Date().toISOString()
});

// Avoid - no context
logger.info('Message sent');
```

### 3. Use Structured Data
```javascript
// Good - structured object
logger.error('API call failed', {
  url: '/api/v1/data',
  method: 'POST',
  status: 500,
  duration: 1500,
  error: error.message
});
```

### 4. Don't Log Sensitive Information
```javascript
// Bad - logs password
logger.info('User login', { username, password });

// Good - logs only safe data
logger.info('User login attempt', { username, timestamp });
```

## Troubleshooting

### No Logs Appearing
1. Check console for errors
2. Verify logger is imported: `import logger from './services/logger'`
3. Check log level configuration
4. Try `window.logger.info('test')` in console

### Performance Issues
1. Reduce log frequency in production
2. Increase `maxLogs` if logs are being dropped
3. Disable verbose performance monitoring
4. Clear logs regularly: `logger.clearLogs()`

### Debug Panel Not Opening
1. Check keyboard shortcut: `Ctrl+Shift+L`
2. Try console command: `window.debugApp.showLogs()`
3. Check for JavaScript errors in console
4. Verify React component is properly imported

## Testing the System

Run the test script in browser console:
```javascript
// Copy and paste the contents of src/test/logging-test.js
// Or use the built-in test
window.debugApp.runTests?.();
```

## File Structure

```
src/
├── services/
│   ├── logger.js              # Main logging service
│   ├── performanceMonitor.js  # Performance tracking
│   └── text2sqlService.js     # API service with logging
├── components/
│   └── Debug/
│       └── LogViewer.js       # Visual log viewer component
├── utils/
│   └── performanceUtils.js    # React performance utilities
└── test/
    └── logging-test.js        # Test script
```

## Support

For issues or questions about the logging system:
1. Check the browser console for errors
2. Review the logs with `window.debugApp.getLogs()`
3. Test basic functionality with the test script
4. Check network connectivity for server-side logging

## Future Enhancements

Planned improvements:
- **Log aggregation** - Send logs to centralized logging service
- **Real-time dashboard** - Web-based log monitoring
- **Alert system** - Notifications for error thresholds
- **Log analysis** - Automatic error pattern detection
- **Performance budgets** - Alerts for performance regressions
