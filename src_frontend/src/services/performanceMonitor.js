import logger from './logger';

class PerformanceMonitor {
  constructor() {
    this.metrics = new Map();
    this.intervals = [];
    this.observers = [];
    
    this.init();
  }

  init() {
    // Monitor page load performance
    if (typeof window !== 'undefined') {
      window.addEventListener('load', () => {
        this.recordPageLoadMetrics();
      });

      // Monitor long tasks
      if ('PerformanceObserver' in window) {
        this.setupPerformanceObservers();
      }

      // Monitor memory usage periodically
      this.startMemoryMonitoring();

      // Monitor network connectivity
      this.setupNetworkMonitoring();
    }
  }

  recordPageLoadMetrics() {
    try {
      const navigation = performance.getEntriesByType('navigation')[0];
      const paint = performance.getEntriesByType('paint');

      const metrics = {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
        pageLoadTime: navigation.loadEventEnd - navigation.fetchStart,
        dnsLookup: navigation.domainLookupEnd - navigation.domainLookupStart,
        tcpConnect: navigation.connectEnd - navigation.connectStart,
        serverResponse: navigation.responseEnd - navigation.requestStart,
        domProcessing: navigation.domComplete - navigation.domInteractive,
        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0
      };

      logger.info('Page Load Performance Metrics', metrics);
      this.recordMetric('pageLoad', metrics);
    } catch (error) {
      logger.error('Failed to record page load metrics', error);
    }
  }

  setupPerformanceObservers() {
    // Long Task Observer
    try {
      const longTaskObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.duration > 50) { // Tasks longer than 50ms
            logger.warn('Long Task Detected', {
              duration: entry.duration,
              startTime: entry.startTime,
              name: entry.name
            });
          }
        });
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });
      this.observers.push(longTaskObserver);
    } catch (error) {
      logger.debug('Long task observer not supported');
    }

    // Largest Contentful Paint Observer
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        logger.info('Largest Contentful Paint', {
          lcp: lastEntry.startTime,
          element: lastEntry.element?.tagName || 'unknown'
        });
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
      this.observers.push(lcpObserver);
    } catch (error) {
      logger.debug('LCP observer not supported');
    }

    // First Input Delay Observer
    try {
      const fidObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          logger.info('First Input Delay', {
            fid: entry.processingStart - entry.startTime,
            eventType: entry.name
          });
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
      this.observers.push(fidObserver);
    } catch (error) {
      logger.debug('FID observer not supported');
    }
  }

  startMemoryMonitoring() {
    const monitorMemory = () => {
      if (performance.memory) {
        const memInfo = {
          usedJSHeapSize: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
          totalJSHeapSize: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024),
          jsHeapSizeLimit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024)
        };

        // Log if memory usage is high
        const memoryUsagePercent = (memInfo.usedJSHeapSize / memInfo.jsHeapSizeLimit) * 100;
        if (memoryUsagePercent > 80) {
          logger.warn('High Memory Usage Detected', {
            ...memInfo,
            usagePercent: Math.round(memoryUsagePercent)
          });
        } else {
          logger.debug('Memory Usage', {
            ...memInfo,
            usagePercent: Math.round(memoryUsagePercent)
          });
        }

        this.recordMetric('memory', memInfo);
      }
    };

    // Monitor every 30 seconds
    const interval = setInterval(monitorMemory, 30000);
    this.intervals.push(interval);

    // Initial measurement
    monitorMemory();
  }

  setupNetworkMonitoring() {
    // Monitor online/offline status
    const logNetworkStatus = () => {
      logger.info('Network Status', {
        online: navigator.onLine,
        connectionType: navigator.connection?.effectiveType || 'unknown',
        downlink: navigator.connection?.downlink || 'unknown',
        rtt: navigator.connection?.rtt || 'unknown'
      });
    };

    window.addEventListener('online', () => {
      logger.success('Network Connection Restored');
      logNetworkStatus();
    });

    window.addEventListener('offline', () => {
      logger.error('Network Connection Lost');
    });

    // Log initial network status
    logNetworkStatus();
  }

  // Start timing an operation
  startTiming(operationName) {
    const startTime = performance.now();
    return {
      end: () => {
        const duration = performance.now() - startTime;
        logger.debug(`Operation Timing: ${operationName}`, { duration: Math.round(duration) });
        this.recordMetric(`timing_${operationName}`, { duration });
        return duration;
      }
    };
  }

  // Record a custom metric
  recordMetric(name, value) {
    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    this.metrics.get(name).push({
      value,
      timestamp: new Date().toISOString()
    });

    // Keep only last 100 entries per metric
    const entries = this.metrics.get(name);
    if (entries.length > 100) {
      entries.splice(0, entries.length - 100);
    }
  }

  // Monitor API call performance
  monitorApiCall(url, method, duration, status) {
    const isSuccess = status >= 200 && status < 300;
    const isSlow = duration > 5000; // 5 seconds

    if (isSlow) {
      logger.warn('Slow API Call Detected', {
        url,
        method,
        duration,
        status
      });
    }

    this.recordMetric('apiCalls', {
      url,
      method,
      duration,
      status,
      success: isSuccess
    });
  }

  // Monitor React component render performance
  monitorComponentRender(componentName, renderTime) {
    if (renderTime > 100) { // 100ms is considered slow
      logger.warn('Slow Component Render', {
        component: componentName,
        renderTime
      });
    }

    this.recordMetric('componentRenders', {
      component: componentName,
      renderTime
    });
  }

  // Get performance summary
  getPerformanceSummary() {
    const summary = {};
    
    for (const [metricName, entries] of this.metrics.entries()) {
      if (entries.length > 0) {
        const latest = entries[entries.length - 1];
        summary[metricName] = {
          latest: latest.value,
          count: entries.length,
          timestamp: latest.timestamp
        };
      }
    }

    return summary;
  }

  // Clean up
  destroy() {
    this.intervals.forEach(interval => clearInterval(interval));
    this.observers.forEach(observer => observer.disconnect());
    this.metrics.clear();
  }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor();

// Add to window for debugging
if (typeof window !== 'undefined') {
  window.performanceMonitor = performanceMonitor;
}

export default performanceMonitor;
