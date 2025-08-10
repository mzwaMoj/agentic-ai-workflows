# Backend-Frontend Integration Strategy

## Overview

This document outlines the architectural pattern used to connect a Python FastAPI backend with a React frontend in a document intelligence application. The strategy can be adapted to similar RAG (Retrieval Augmented Generation) or AI-powered search applications.

## Architecture Pattern

### Core Components

```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐
│   React Frontend│ ◄─────────────────► │ Python FastAPI  │
│   (Port 3000)   │                     │   (Port 7071)   │
└─────────────────┘                     └─────────────────┘
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │  Azure Services │
                                        │ • Cognitive     │
                                        │   Search        │
                                        │ • OpenAI        │
                                        │ • Blob Storage  │
                                        └─────────────────┘
```

## 1. API Endpoint Structure

### Standard REST Pattern
- **Base URL**: `http://localhost:7071/api`
- **Content-Type**: `application/json`
- **Response Format**: Consistent JSON structures

### Core Endpoint Categories

#### Health & Status Endpoints
```
GET /api/health              - Basic health check
GET /api/health/detailed     - Detailed service status
GET /api/health/ready        - Readiness probe
GET /api/health/live         - Liveness check
```

#### Search & Retrieval Endpoints
```
POST /api/search             - Document search with filters
GET  /api/search/stats       - Search statistics
GET  /api/search/document/{id} - Get specific document
POST /api/search/facets      - Get search facets
```

#### AI Processing Endpoints
```
POST /api/ai/interpret       - AI query interpretation
POST /api/ai/insights        - Generate document insights
GET  /api/ai/status          - AI service status
POST /api/ai/chat/completions - Direct AI completions
```

#### Utility Endpoints
```
GET /api/suggestions?q={query} - Search suggestions
GET /api/documents/stats       - Document statistics
```

## 2. Request/Response Patterns

### Standard Request Structure
```javascript
// Frontend request pattern
const response = await fetch(`${API_BASE_URL}/api/endpoint`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: "user input",
    parameters: {...},
    filters: {...}
  })
});
```

### Standard Response Structure
```json
{
  "status": "success|error",
  "data": {...},
  "message": "optional message",
  "executionTimeMs": 123.45,
  "timestamp": "2024-07-24T10:00:00Z"
}
```

## 3. Frontend Integration Pattern

### Service Layer Architecture
```javascript
// services/apiService.js
class ApiService {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Specific service methods
  async searchDocuments(query, filters = {}) {
    return this.makeRequest('/api/search', {
      method: 'POST',
      body: JSON.stringify({ query, filters })
    });
  }

  async getHealthStatus() {
    return this.makeRequest('/api/health');
  }

  async interpretResults(query, searchResults) {
    return this.makeRequest('/api/ai/interpret', {
      method: 'POST',
      body: JSON.stringify({ query, searchResults })
    });
  }
}
```

### React Component Integration
```javascript
// components/SearchInterface.js
import { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';

function SearchInterface() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const searchResults = await apiService.searchDocuments(query);
      setResults(searchResults.data || []);
      
      // Optional: Get AI interpretation
      if (searchResults.data?.length > 0) {
        const interpretation = await apiService.interpretResults(
          query, 
          searchResults.data
        );
        // Handle interpretation...
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search documents..."
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      
      {error && <div className="error">{error}</div>}
      {results.map(result => (
        <div key={result.id}>{result.title}</div>
      ))}
    </div>
  );
}
```

## 4. Error Handling Strategy

### Backend Error Responses
```python
# FastAPI error handling
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

### Frontend Error Handling
```javascript
// Error handling in React
const [error, setError] = useState(null);

try {
  const result = await apiService.searchDocuments(query);
  // Handle success
} catch (err) {
  if (err.message.includes('HTTP 503')) {
    setError('Service temporarily unavailable. Please try again.');
  } else if (err.message.includes('HTTP 422')) {
    setError('Invalid request. Please check your input.');
  } else {
    setError('An unexpected error occurred.');
  }
}
```

## 5. State Management Pattern

### Centralized State (using Context or Redux)
```javascript
// context/AppContext.js
const AppContext = createContext();

export function AppProvider({ children }) {
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [interpretation, setInterpretation] = useState('');

  const performSearch = async (query) => {
    setLoading(true);
    setError(null);
    
    try {
      const results = await apiService.searchDocuments(query);
      setSearchResults(results.data);
      
      const aiResult = await apiService.interpretResults(query, results.data);
      setInterpretation(aiResult.answer);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppContext.Provider value={{
      searchResults,
      loading,
      error,
      interpretation,
      performSearch
    }}>
      {children}
    </AppContext.Provider>
  );
}
```

## 6. Configuration Management

### Environment-Based Configuration
```javascript
// config/apiConfig.js
const config = {
  development: {
    apiBaseUrl: 'http://localhost:7071',
    timeout: 30000,
    retryAttempts: 3
  },
  production: {
    apiBaseUrl: process.env.REACT_APP_API_URL,
    timeout: 60000,
    retryAttempts: 5
  }
};

export const apiConfig = config[process.env.NODE_ENV] || config.development;
```

## 7. Performance Optimization

### Request Optimization
```javascript
// Debounced search for suggestions
import { debounce } from 'lodash';

const debouncedGetSuggestions = debounce(async (query) => {
  if (query.length > 2) {
    const suggestions = await apiService.getSuggestions(query);
    setSuggestions(suggestions.data);
  }
}, 300);

// Caching frequently accessed data
const cache = new Map();

async function cachedRequest(endpoint, options) {
  const cacheKey = `${endpoint}-${JSON.stringify(options)}`;
  
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }
  
  const result = await apiService.makeRequest(endpoint, options);
  cache.set(cacheKey, result);
  
  return result;
}
```

### Loading States
```javascript
// Progressive loading for better UX
function SearchResults() {
  const [initialLoading, setInitialLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [interpretation, setInterpretation] = useState('');

  const handleSearch = async (query) => {
    // Show search results immediately
    setInitialLoading(true);
    const searchResults = await apiService.searchDocuments(query);
    setResults(searchResults.data);
    setInitialLoading(false);
    
    // Get AI interpretation in background
    setAiLoading(true);
    const aiResult = await apiService.interpretResults(query, searchResults.data);
    setInterpretation(aiResult.answer);
    setAiLoading(false);
  };

  return (
    <div>
      {initialLoading ? (
        <div>Searching documents...</div>
      ) : (
        <>
          <ResultsList results={results} />
          {aiLoading ? (
            <div>Generating AI insights...</div>
          ) : (
            <InterpretationPanel text={interpretation} />
          )}
        </>
      )}
    </div>
  );
}
```

## 8. Security Considerations

### Request Security
```javascript
// CORS handling (Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

// Request validation (Frontend)
function validateRequest(data) {
  if (!data.query || typeof data.query !== 'string') {
    throw new Error('Invalid query parameter');
  }
  
  if (data.query.length > 1000) {
    throw new Error('Query too long');
  }
  
  return true;
}
```

## 9. Testing Strategy

### Backend Testing
```python
# test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_search_endpoint():
    response = client.post("/api/search", json={
        "query": "test query",
        "top": 5
    })
    assert response.status_code == 200
    assert "results" in response.json()
```

### Frontend Testing
```javascript
// ApiService.test.js
import { apiService } from '../services/apiService';

describe('ApiService', () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  test('should handle successful search', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: [{ id: 1, title: 'Test Doc' }] })
    });

    const result = await apiService.searchDocuments('test query');
    expect(result.data).toHaveLength(1);
    expect(result.data[0].title).toBe('Test Doc');
  });

  test('should handle API errors', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 503,
      statusText: 'Service Unavailable'
    });

    await expect(apiService.searchDocuments('test'))
      .rejects.toThrow('HTTP 503: Service Unavailable');
  });
});
```

## 10. Deployment Considerations

### Development vs Production
```javascript
// Different configurations for different environments
const apiConfigs = {
  development: {
    baseUrl: 'http://localhost:7071',
    timeout: 30000
  },
  staging: {
    baseUrl: 'https://staging-api.example.com',
    timeout: 45000
  },
  production: {
    baseUrl: 'https://api.example.com',
    timeout: 60000
  }
};
```

## Key Takeaways for Similar Projects

1. **Consistent API Design**: Use RESTful endpoints with predictable patterns
2. **Error Handling**: Implement comprehensive error handling on both ends
3. **Progressive Loading**: Show results incrementally for better UX
4. **Service Layer**: Abstract API calls into reusable service classes
5. **State Management**: Centralize application state for complex interactions
6. **Performance**: Use caching, debouncing, and progressive loading
7. **Testing**: Test both API endpoints and frontend integration
8. **Configuration**: Environment-based configuration for different deployments

This pattern works well for AI-powered applications that need to:
- Search and retrieve documents
- Process results with AI services
- Provide real-time user feedback
- Handle multiple data sources
- Scale across different environments