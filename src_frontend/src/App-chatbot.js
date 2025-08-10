import React from 'react';
import ChatBot from './components/ChatBot';
import './App-chatbot.css';

function App() {
  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>Standard Bank Compliance Assistant</h1>
          <p>Ask questions about regulations, compliance, and amendments</p>
        </div>
      </header>
      
      <main className="app-main">
        <ChatBot />
      </main>
      
      <footer className="app-footer">
        <p>&copy; 2025 Standard Bank. Compliance Assistant powered by AI.</p>
      </footer>
    </div>
  );
}

export default App;
