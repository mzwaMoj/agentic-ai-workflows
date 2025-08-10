/**
 * Frontend Logging Test Script
 * Run this in the browser console to test logging functionality
 */

console.log('%c🧪 Testing Frontend Logging System...', 'color: #FF9800; font-size: 16px; font-weight: bold;');

// Test basic logging levels
logger.debug('This is a debug message', { testData: 'debug info' });
logger.info('This is an info message', { testData: 'info data' });
logger.success('This is a success message', { testData: 'success data' });
logger.warn('This is a warning message', { testData: 'warning data' });
logger.error('This is an error message', new Error('Test error'));

// Test API call logging
logger.apiCall('GET', 'https://api.test.com/data', { param: 'test' });
logger.apiResponse('GET', 'https://api.test.com/data', 200, { result: 'success' }, 150);

// Test user action logging
logger.userAction('Button Click', { button: 'Test Button', location: 'Header' });

// Test component lifecycle logging
logger.componentMount('TestComponent', { props: { test: true } });
logger.componentUnmount('TestComponent');

// Test performance monitoring
const timer = performanceMonitor.startTiming('test-operation');
setTimeout(() => {
  timer.end();
  console.log('%c✅ Logging tests completed!', 'color: #4CAF50; font-weight: bold;');
  console.log('%cCheck the logs with: window.debugApp.getLogs()', 'color: #2196F3;');
}, 100);

// Test memory and performance metrics
console.log('%c📊 Performance Summary:', 'color: #9C27B0; font-weight: bold;');
console.log(performanceMonitor.getPerformanceSummary());
