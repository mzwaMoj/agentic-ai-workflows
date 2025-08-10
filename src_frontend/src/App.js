import React, { useEffect, useState } from 'react';
import ChatBot from './components/ChatBot/ChatBotSimple';
import LogViewer from './components/Debug/LogViewer';
import logger from './services/logger';
import performanceMonitor from './services/performanceMonitor';
import './App-chatbot.css';

function App() {
  const [showDebugPanel, setShowDebugPanel] = useState(false);

  useEffect(() => {
    logger.componentMount('App', {
      environment: process.env.NODE_ENV,
      userAgent: navigator.userAgent.substring(0, 100),
      url: window.location.href
    });
    
    logger.info('Text2SQL AI Analyst started', {
      version: process.env.REACT_APP_VERSION || 'unknown',
      buildTime: process.env.REACT_APP_BUILD_TIME || 'unknown'
    });

    // Add keyboard shortcut for debug panel (Ctrl+Shift+L)
    const handleKeyPress = (event) => {
      if (event.ctrlKey && event.shiftKey && event.key === 'L') {
        event.preventDefault();
        setShowDebugPanel(prev => {
          const newState = !prev;
          logger.info(`Debug panel ${newState ? 'opened' : 'closed'} via keyboard shortcut`);
          return newState;
        });
      }
    };

    window.addEventListener('keydown', handleKeyPress);    // Add debug functions to window for console access
    window.debugApp = {
      showLogs: () => setShowDebugPanel(true),
      hideLogs: () => setShowDebugPanel(false),
      getLogs: () => logger.getAllLogs(),
      clearLogs: () => logger.clearLogs(),
      downloadLogs: () => logger.downloadLogs(),
      getPerformance: () => performanceMonitor.getPerformanceSummary(),
      startTiming: (name) => performanceMonitor.startTiming(name)
    };    logger.info('Debug functions added to window.debugApp', {
      functions: ['showLogs', 'hideLogs', 'getLogs', 'clearLogs', 'downloadLogs', 'getPerformance', 'startTiming']
    });

    return () => {
      window.removeEventListener('keydown', handleKeyPress);
      delete window.debugApp;
      logger.componentUnmount('App');
    };
  }, []);  return (
    <div className="App">
      <main className="app-main">
        <ChatBot />
      </main>

      {/* Hidden Debug Panel */}
      <LogViewer 
        isVisible={showDebugPanel} 
        onClose={() => setShowDebugPanel(false)} 
      />
    </div>
  );
}

export default App;
