# Agentic AI Lessons - Directory Structure Plan

## Proposed Directory Structure

```
ai-agents-lessons/
│
├── README.md                          # Course overview and setup instructions
├── agentic-lessons-plan.md            # Your existing detailed lesson plan
├── requirements.txt                   # Core dependencies for all lessons (OpenAI, FastAPI, etc.)
│
├── data/                              # Shared data files used across multiple lessons
│   ├── documents/                     # Documents for RAG examples
│   ├── databases/                     # SQLite databases for the SQL lesson
│   └── test-cases/                    # Test cases for evaluation
│
├── utils/                             # Shared utility scripts
│   ├── api_utils.py                   # Common API interaction utilities
│   ├── evaluation.py                  # MLflow-based evaluation utilities
│   └── visualization.py               # Visualization utilities
│
├── lesson_1_environment_setup/
│   ├── README.md                      # Lesson overview and objectives
│   ├── lesson_1_notebook.ipynb        # Main interactive notebook
│   ├── examples/                      # Additional examples
│   └── exercises/                     # Practice exercises
│
├── lesson_2_chatbot_basics/
│   ├── README.md
│   ├── lesson_2_notebook.ipynb
│   ├── examples/
│   └── exercises/
│
├── lesson_3_rag_web_access/
│   ├── README.md
│   ├── lesson_3_notebook.ipynb
│   ├── examples/
│   └── exercises/
│
├── lesson_4_text_to_sql/
│   ├── README.md
│   ├── lesson_4_notebook.ipynb
│   ├── examples/
│   ├── exercises/
│   └── sample_database.sqlite         # Sample database for this lesson
│
├── lesson_5_document_rag/
│   ├── README.md
│   ├── lesson_5_notebook.ipynb        # Using LlamaIndex
│   ├── examples/
│   ├── exercises/
│   └── sample_documents/              # Sample documents for this lesson
│
├── lesson_6_multilingual_agents/
│   ├── README.md
│   ├── lesson_6_notebook.ipynb        # Using Docling
│   ├── examples/
│   └── exercises/
│
├── lesson_7_multi_agent_systems/
│   ├── README.md
│   ├── lesson_7_notebook.ipynb
│   ├── examples/
│   └── exercises/
│
├── lesson_8_evaluation_metrics/
│   ├── README.md
│   ├── lesson_8_notebook.ipynb        # Using MLflow for tracking metrics
│   ├── examples/
│   └── evaluation_datasets/           # Sample evaluation datasets
│
├── lesson_9_api_deployment/
│   ├── README.md
│   ├── lesson_9_notebook.ipynb
│   ├── app.py                         # FastAPI application
│   ├── examples/
│   └── exercises/
│
└── lesson_10_production/
    ├── README.md
    ├── lesson_10_notebook.ipynb       # Using MLflow for model registry and deployment
    ├── Dockerfile                     # Sample Dockerfile
    ├── docker-compose.yml             # Sample docker-compose file
    ├── examples/
    └── exercises/
```

## Structure Details

1. **Root Directory**:
   - `README.md`: Main course documentation with setup instructions
   - `requirements.txt`: Core dependencies for all lessons
   - `agentic-lessons-plan.md`: Your detailed lesson plan

2. **Shared Resources**:
   - `data/`: Shared data files used across lessons
   - `utils/`: Shared utility scripts for common functions

3. **Lesson Directories**:
   - Each lesson has its own directory with consistent structure
   - Each contains a README.md with overview and objectives
   - Main content delivered via an interactive Jupyter notebook
   - Examples and exercises folders for additional materials
   - Lesson-specific resources as needed (databases, documents, etc.)

4. **Consistent Lesson Structure**:
   - Each lesson README.md will follow a standard template
   - Each notebook will have a standard structure:
     - Introduction and objectives
     - Prerequisites
     - Theoretical concepts
     - Code examples
     - Hands-on exercises
     - Summary and next steps

## Implementation Plan

Implementation steps:

1. Create the directory structure
2. Generate template README.md files for each lesson
3. Create starter notebook templates for each lesson
4. Develop any necessary sample data and utility files

This structure allows for:
- Clear organization by lesson topic
- Consistent learning experience across lessons
- Easy navigation for learners
- Modularity for future updates or extensions
- Sharing of common resources across lessons

## Key Libraries by Lesson

1. **Lesson 1**: OpenAI SDK, python-dotenv
2. **Lesson 2**: OpenAI SDK, requests
3. **Lesson 3**: OpenAI SDK, BraveSearch, Firecrawl
4. **Lesson 4**: OpenAI SDK, SQLite
5. **Lesson 5**: OpenAI SDK, LlamaIndex
6. **Lesson 6**: OpenAI SDK, Docling
7. **Lesson 7**: OpenAI SDK, custom code (with brief conceptual overview of frameworks)
8. **Lesson 8**: OpenAI SDK, MLflow
9. **Lesson 9**: OpenAI SDK, FastAPI
10. **Lesson 10**: OpenAI SDK, FastAPI, MLflow, Docker
