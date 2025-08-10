import React from 'react';
import performanceMonitor from '../services/performanceMonitor';

// Higher-order component to monitor React component performance
export const withPerformanceMonitoring = (WrappedComponent, componentName) => {
  return React.forwardRef((props, ref) => {
    const renderStart = performance.now();
    
    React.useEffect(() => {
      const renderTime = performance.now() - renderStart;
      performanceMonitor.monitorComponentRender(componentName || WrappedComponent.name, renderTime);
    });

    return <WrappedComponent {...props} ref={ref} />;
  });
};

// Hook to measure component render time
export const useRenderTime = (componentName) => {
  const renderStart = React.useRef(performance.now());
  
  React.useEffect(() => {
    const renderTime = performance.now() - renderStart.current;
    performanceMonitor.monitorComponentRender(componentName, renderTime);
    renderStart.current = performance.now(); // Reset for next render
  });
};

// Hook to measure operation timing
export const useOperationTiming = () => {
  return React.useCallback((operationName) => {
    return performanceMonitor.startTiming(operationName);
  }, []);
};

export default {
  withPerformanceMonitoring,
  useRenderTime,
  useOperationTiming
};
