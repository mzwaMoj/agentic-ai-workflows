# Backend-Frontend Integration Plan: Text2SQL Agent with React UI

## Overview

This document outlines the comprehensive integration strategy for connecting the **Python FastAPI Text2SQL backend** with the **React frontend** to create a seamless data analysis application with chart visualization capabilities.

### Current Architecture Assessment

#### Backend (Python FastAPI)
- **Location**: `app/` directory
- **Port**: 8000 (configured in .env)
- **Main Entry**: `app/main.py`
- **Key Features**:
  - Natural language to SQL conversion
  - SQL query execution
  - Interactive chart generation (Plotly-based)
  - Chat-based interactions
  - Multiple database support (SQL Server)

#### Frontend (React)
- **Location**: `src_frontend/` directory
- **Current State**: Configured for compliance chatbot (needs adaptation)
- **Key Components**: ChatBot, ResultDisplay, SearchInterface
- **Service Layer**: Basic chatService.js (needs extension)

---

## 1. Integration Architecture

### System Overview
```
┌─────────────────────┐    HTTP/REST API    ┌─────────────────────┐
│   React Frontend    │ ◄─────────────────► │ Python FastAPI      │
│   (Port 3000)       │                     │   (Port 8000)       │
│   • Chat Interface  │                     │ • Text2SQL Engine   │
│   • Chart Display   │                     │ • SQL Execution     │
│   • Result Tables   │                     │ • Chart Generation  │
│   • Error Handling  │                     │ • Data Processing   │
└─────────────────────┘                     └─────────────────────┘
                                                      │
                                                      ▼
                                              ┌─────────────────────┐
                                              │   SQL Server DB     │
                                              │ • Customer Data     │
                                              │ • Transaction Data  │
                                              │ • Account Info      │
                                              └─────────────────────┘
```

### Core API Endpoints to Integrate

#### 1. Primary Text2SQL Endpoint
```
POST /api/v1/text2sql/generate
```
**Purpose**: Main endpoint for natural language queries with chart generation
**Request**: 
```json
{
  "query": "Show me customer balances by income category",
  "include_charts": true,
  "max_results": 100,
  "chat_history": [...]
}
```
**Response**:
```json
{
  "success": true,
  "response": "Here are the customer balances...",
  "sql_query": "SELECT income_category, AVG(balance)...",
  "sql_results": [...],
  "chart_html": "<div id='plotly-chart'>...</div>",
  "execution_time": 2.34,
  "chat_history": [...]
}
```

#### 2. Chart Viewer Endpoint
```
POST /api/v1/text2sql/generate-chart
```
**Purpose**: Direct HTML chart viewer for testing
**Returns**: Complete HTML page with embedded chart

#### 3. Health Check Endpoints
```
GET /api/v1/health
GET /api/v1/health/detailed
```

#### 4. SQL Validation
```
POST /api/v1/text2sql/validate
```

#### 5. Table Information
```
GET /api/v1/text2sql/tables
```

---

## 2. Frontend Adaptation Strategy

### 2.1 Service Layer Enhancement

#### Current State Analysis
- Existing `chatService.js` points to incorrect endpoints
- Configuration needs update for text2sql backend
- Missing chart handling capabilities

#### New Service Architecture
```javascript
// services/text2sqlService.js
class Text2SqlService {
  async generateSQL(query, options = {}) {
    // Main text2sql generation
  }
  
  async validateQuery(query) {
    // Query validation
  }
  
  async getTableInfo() {
    // Available tables
  }
  
  async getSuggestions() {
    // Query suggestions
  }
}

// services/chartService.js  
class ChartService {
  async renderChart(chartHtml, containerId) {
    // Render Plotly charts in React
  }
  
  async downloadChart(chartHtml, format) {
    // Export chart functionality
  }
}
```

### 2.2 Component Architecture Updates

#### Enhanced Chat Interface
```
components/
├── ChatBot/
│   ├── ChatBot.js           # Main chat interface
│   ├── ChatMessage.js       # Individual messages
│   ├── ChatInput.js         # User input
│   └── TypingIndicator.js   # Loading states
├── Results/
│   ├── ResultsContainer.js  # Main results wrapper
│   ├── SQLResultTable.js    # Data table display
│   ├── ChartViewer.js       # Chart rendering ⭐ NEW
│   └── QueryInfo.js         # SQL query display
├── Charts/
│   ├── PlotlyChart.js       # Plotly integration ⭐ NEW
│   ├── ChartControls.js     # Chart interaction ⭐ NEW
│   └── ChartExport.js       # Export functionality ⭐ NEW
└── Shared/
    ├── LoadingSpinner.js
    ├── ErrorBoundary.js
    └── APIStatus.js
```

### 2.3 Chart Integration Strategy

#### Challenge: Plotly HTML to React
The backend generates complete Plotly HTML strings. We need to safely render these in React.

#### Solution: HTML Parser + Plotly React
```javascript
// components/Charts/PlotlyChart.js
import Plotly from 'plotly.js-dist';
import { useEffect, useRef } from 'react';

function PlotlyChart({ chartHtml, containerId }) {
  const chartRef = useRef(null);
  
  useEffect(() => {
    if (chartHtml && chartRef.current) {
      // Extract Plotly data and layout from HTML
      const plotlyData = extractPlotlyData(chartHtml);
      
      // Render with Plotly.js
      Plotly.newPlot(chartRef.current, plotlyData.data, plotlyData.layout, {
        responsive: true,
        displayModeBar: true
      });
    }
  }, [chartHtml]);
  
  return <div ref={chartRef} className="plotly-chart" />;
}
```

#### Alternative: IFrame Approach
```javascript
// For quick implementation
function ChartIframe({ chartHtml }) {
  const srcDoc = `
    <!DOCTYPE html>
    <html>
    <head>
      <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body style="margin:0;">
      ${chartHtml}
    </body>
    </html>
  `;
  
  return (
    <iframe 
      srcDoc={srcDoc}
      width="100%" 
      height="500px"
      frameBorder="0"
    />
  );
}
```

---

## 3. Implementation Roadmap

### Phase 1: Backend API Verification ✅
**Status**: Already working based on test files
- [x] Text2SQL endpoint functional
- [x] Chart generation working
- [x] Health checks operational
- [x] Error handling implemented

### Phase 2: Service Layer Integration (Week 1)

#### 2.1 Update API Configuration
```javascript
// config/apiConfig.js
const config = {
  development: {
    baseURL: 'http://localhost:8000',
    timeout: 60000,
    endpoints: {
      generateSQL: '/api/v1/text2sql/generate',
      validateQuery: '/api/v1/text2sql/validate',
      health: '/api/v1/health',
      tables: '/api/v1/text2sql/tables'
    }
  },
  production: {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    timeout: 120000,
    endpoints: { /* same as development */ }
  }
};
```

#### 2.2 Create Text2SQL Service
```javascript
// services/text2sqlService.js
class Text2SqlService {
  constructor(config) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout;
    this.endpoints = config.endpoints;
  }

  async generateSQL(query, options = {}) {
    const payload = {
      query,
      include_charts: options.includeCharts ?? true,
      max_results: options.maxResults ?? 100,
      chat_history: options.chatHistory ?? []
    };

    try {
      const response = await fetch(`${this.baseURL}${this.endpoints.generateSQL}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(this.timeout)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Text2SQL generation failed:', error);
      throw this.handleError(error);
    }
  }

  handleError(error) {
    if (error.name === 'TimeoutError') {
      return new Error('Query timeout - please try a simpler request');
    }
    if (error.message.includes('500')) {
      return new Error('Server error - please try again later');
    }
    return error;
  }
}
```

#### 2.3 Update ChatBot Component
```javascript
// components/ChatBot/ChatBot.js
import { useState, useEffect } from 'react';
import { text2sqlService } from '../../services/text2sqlService';
import ChartViewer from '../Charts/ChartViewer';
import SQLResultTable from '../Results/SQLResultTable';

function ChatBot() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentResults, setCurrentResults] = useState(null);

  const handleSendMessage = async (messageText) => {
    // Add user message
    const userMessage = {
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Get chat history for context
      const chatHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // Call text2sql service
      const response = await text2sqlService.generateSQL(messageText, {
        chatHistory,
        includeCharts: true,
        maxResults: 100
      });

      // Add assistant response
      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
        sqlQuery: response.sql_query,
        sqlResults: response.sql_results,
        chartHtml: response.chart_html,
        executionTime: response.execution_time
      };

      setMessages(prev => [...prev, assistantMessage]);
      setCurrentResults(response);

    } catch (error) {
      // Handle errors gracefully
      const errorMessage = {
        role: 'assistant',
        content: `I apologize, but I encountered an error: ${error.message}`,
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="messages-container">
        {messages.map((message, index) => (
          <ChatMessage 
            key={index} 
            message={message}
            showChart={message.chartHtml}
            showTable={message.sqlResults}
          />
        ))}
        {isLoading && <TypingIndicator />}
      </div>
      
      <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      
      {currentResults && (
        <ResultsContainer results={currentResults} />
      )}
    </div>
  );
}
```

### Phase 3: Chart Integration (Week 2)

#### 3.1 Chart Viewer Component
```javascript
// components/Charts/ChartViewer.js
import { useEffect, useRef, useState } from 'react';

function ChartViewer({ chartHtml, title }) {
  const [renderMethod, setRenderMethod] = useState('iframe'); // 'iframe' or 'plotly'
  const chartRef = useRef(null);

  const renderIframe = () => {
    const srcDoc = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
          body { margin: 0; font-family: Arial, sans-serif; }
          .chart-container { padding: 10px; }
        </style>
      </head>
      <body>
        <div class="chart-container">
          ${chartHtml}
        </div>
      </body>
      </html>
    `;

    return (
      <iframe
        srcDoc={srcDoc}
        width="100%"
        height="500px"
        frameBorder="0"
        title={title || "Data Visualization"}
        className="chart-iframe"
      />
    );
  };

  return (
    <div className="chart-viewer">
      {title && <h3 className="chart-title">{title}</h3>}
      {chartHtml ? renderIframe() : (
        <div className="no-chart">No visualization available</div>
      )}
    </div>
  );
}
```

#### 3.2 Enhanced Message Component
```javascript
// components/ChatBot/ChatMessage.js
import ChartViewer from '../Charts/ChartViewer';
import SQLResultTable from '../Results/SQLResultTable';

function ChatMessage({ message, showChart, showTable }) {
  return (
    <div className={`message message-${message.role}`}>
      <div className="message-content">
        <p>{message.content}</p>
        
        {message.sqlQuery && (
          <details className="sql-query-details">
            <summary>View SQL Query</summary>
            <pre><code>{message.sqlQuery}</code></pre>
          </details>
        )}
        
        {showChart && message.chartHtml && (
          <div className="message-chart">
            <ChartViewer 
              chartHtml={message.chartHtml}
              title="Data Visualization"
            />
          </div>
        )}
        
        {showTable && message.sqlResults && (
          <div className="message-table">
            <SQLResultTable 
              data={message.sqlResults}
              maxRows={10}
            />
          </div>
        )}
        
        {message.executionTime && (
          <div className="execution-info">
            <small>⚡ Executed in {message.executionTime.toFixed(2)}s</small>
          </div>
        )}
      </div>
      
      <div className="message-timestamp">
        {new Date(message.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
}
```

### Phase 4: UI/UX Enhancement (Week 3)

#### 4.1 Results Container
```javascript
// components/Results/ResultsContainer.js
function ResultsContainer({ results }) {
  const [activeTab, setActiveTab] = useState('chart');
  
  if (!results || !results.success) return null;

  return (
    <div className="results-container">
      <div className="results-tabs">
        {results.chart_html && (
          <button 
            className={`tab ${activeTab === 'chart' ? 'active' : ''}`}
            onClick={() => setActiveTab('chart')}
          >
            📊 Chart
          </button>
        )}
        {results.sql_results && (
          <button 
            className={`tab ${activeTab === 'table' ? 'active' : ''}`}
            onClick={() => setActiveTab('table')}
          >
            📋 Data
          </button>
        )}
        {results.sql_query && (
          <button 
            className={`tab ${activeTab === 'sql' ? 'active' : ''}`}
            onClick={() => setActiveTab('sql')}
          >
            🔍 SQL
          </button>
        )}
      </div>

      <div className="tab-content">
        {activeTab === 'chart' && results.chart_html && (
          <ChartViewer chartHtml={results.chart_html} />
        )}
        
        {activeTab === 'table' && results.sql_results && (
          <SQLResultTable data={results.sql_results} />
        )}
        
        {activeTab === 'sql' && results.sql_query && (
          <div className="sql-display">
            <pre><code>{results.sql_query}</code></pre>
          </div>
        )}
      </div>
    </div>
  );
}
```

#### 4.2 Application Layout Update
```javascript
// App.js
import React from 'react';
import ChatBot from './components/ChatBot/ChatBot';
import APIStatus from './components/Shared/APIStatus';
import ErrorBoundary from './components/Shared/ErrorBoundary';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <header className="app-header">
          <div className="header-content">
            <h1>🤖 SQL Analytics Assistant</h1>
            <p>Ask questions about your data and get instant insights with charts</p>
            <APIStatus />
          </div>
        </header>
        
        <main className="app-main">
          <ChatBot />
        </main>
        
        <footer className="app-footer">
          <p>&copy; 2025 Standard Bank. Text2SQL Analytics powered by AI.</p>
        </footer>
      </div>
    </ErrorBoundary>
  );
}
```

---

## 4. Technical Implementation Details

### 4.1 Environment Configuration

#### Backend (.env)
```bash
# Already configured
HOST = 127.0.0.1
PORT = 8000
REACT_APP_API_ENDPOINT=http://localhost:8000/api
```

#### Frontend (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=120000
REACT_APP_CHART_ENABLED=true
REACT_APP_MAX_RESULTS=100
```

### 4.2 CORS Configuration
Ensure backend allows frontend origin:
```python
# app/main.py - already configured
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.3 Error Handling Strategy

#### Backend Error Format
```json
{
  "success": false,
  "error": "Query validation failed",
  "details": "Invalid table name 'xyz'",
  "error_code": "VALIDATION_ERROR"
}
```

#### Frontend Error Handling
```javascript
// utils/errorHandler.js
export const handleAPIError = (error) => {
  if (error.message.includes('timeout')) {
    return 'Query took too long to execute. Please try a simpler request.';
  }
  
  if (error.message.includes('500')) {
    return 'Server error occurred. Please try again later.';
  }
  
  if (error.message.includes('400')) {
    return 'Invalid request. Please check your query and try again.';
  }
  
  return 'An unexpected error occurred. Please contact support.';
};
```

---

## 5. Testing Strategy

### 5.1 Integration Testing
```javascript
// tests/integration/text2sql.test.js
describe('Text2SQL Integration', () => {
  test('should generate SQL and charts', async () => {
    const service = new Text2SqlService(config.development);
    
    const result = await service.generateSQL(
      'Show me customer balances by income category'
    );
    
    expect(result.success).toBe(true);
    expect(result.sql_query).toContain('SELECT');
    expect(result.chart_html).toContain('plotly');
  });
});
```

### 5.2 Component Testing
```javascript
// tests/components/ChatBot.test.js
describe('ChatBot Component', () => {
  test('should display chart when provided', () => {
    const mockMessage = {
      role: 'assistant',
      content: 'Here are the results',
      chartHtml: '<div>mock chart</div>'
    };
    
    render(<ChatMessage message={mockMessage} showChart={true} />);
    expect(screen.getByText('Data Visualization')).toBeInTheDocument();
  });
});
```

---

## 6. Deployment Considerations

### 6.1 Development Setup
```bash
# Backend (Terminal 1)
cd app
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Frontend (Terminal 2)  
cd src_frontend
npm install
npm start  # Runs on port 3000
```

### 6.2 Production Deployment
- Backend: Docker container with Python FastAPI
- Frontend: Build static files and serve via nginx
- API Gateway: Route /api/* to backend, /* to frontend

---

## 7. Success Metrics

### 7.1 Functional Requirements ✅
- [x] Natural language query processing
- [x] SQL generation and execution
- [x] Interactive chart generation
- [x] Chat-based conversation flow
- [ ] Seamless frontend integration
- [ ] Error handling and recovery
- [ ] Performance optimization

### 7.2 User Experience Goals
- Query response time < 10 seconds
- Chart rendering < 2 seconds
- Intuitive chat interface
- Mobile-responsive design
- Accessibility compliance

---

## 8. Risk Mitigation

### 8.1 Technical Risks
- **Chart Rendering**: Use iframe fallback if Plotly integration fails
- **API Timeouts**: Implement progressive loading and timeout handling
- **Memory Issues**: Limit result set size and implement pagination

### 8.2 Security Considerations
- Validate all user inputs
- Sanitize chart HTML before rendering
- Implement rate limiting
- Secure database connections

---

## 9. Next Steps

### Immediate Actions (This Week)
1. ✅ Create this integration plan
2. Update frontend service configuration
3. Implement Text2SqlService class
4. Create ChartViewer component
5. Test basic integration

### Short Term (Next 2 Weeks)
1. Complete UI component updates
2. Implement comprehensive error handling
3. Add loading states and progress indicators
4. Performance optimization
5. User acceptance testing

### Long Term (Next Month)
1. Advanced chart interactions
2. Export functionality
3. Query history and favorites
4. Performance analytics
5. Production deployment

---

## Conclusion

This integration plan provides a comprehensive roadmap for connecting your sophisticated Text2SQL backend with a modern React frontend. The approach prioritizes:

1. **Minimal Backend Changes**: Leverage existing working API endpoints
2. **Progressive Enhancement**: Start with basic integration, add advanced features iteratively  
3. **Robust Error Handling**: Graceful degradation when components fail
4. **Chart-First Experience**: Make data visualization a core part of the user experience
5. **Maintainable Architecture**: Clean separation of concerns and reusable components

The plan addresses the unique challenge of rendering Plotly charts generated by the backend in the React frontend, providing both iframe and native integration options.

**Estimated Timeline**: 3-4 weeks for full integration
**Key Milestone**: Working chat interface with chart display within 1 week
