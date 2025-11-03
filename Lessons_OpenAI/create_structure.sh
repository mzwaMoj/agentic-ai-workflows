#!/bin/bash

# Create the root directory
mkdir -p "ai-agents-lessons"

# Navigate into the root directory
cd "ai-agents-lessons"

# Create core files
touch "README.md"
touch "agentic-lessons-plan.md"
touch "requirements.txt"

# Create data directory and subdirectories
mkdir -p "data/documents"
mkdir -p "data/databases"
mkdir -p "data/test-cases"

# Create utils directory and files
mkdir -p "utils"
touch "utils/api_utils.py"
touch "utils/evaluation.py"
touch "utils/visualization.py"

# Function to create lesson directories and common files
create_lesson() {
    local lesson_name=$1
    mkdir -p "$lesson_name"
    touch "${lesson_name}/README.md"
    # Derive notebook name from lesson_name (e.g., lesson_1_environment_setup -> lesson_1_notebook.ipynb)
    notebook_name=$(echo "$lesson_name" | sed 's/_environment_setup//;s/_chatbot_basics//;s/_rag_web_access//;s/_text_to_sql//;s/_document_rag//;s/_multilingual_agents//;s/_multi_agent_systems//;s/_evaluation_metrics//;s/_api_deployment//;s/_production//')
    touch "${lesson_name}/${notebook_name}_notebook.ipynb"
    mkdir -p "${lesson_name}/examples"
    mkdir -p "${lesson_name}/exercises"
}

# Create lesson directories and files
create_lesson "lesson_1_environment_setup"
# The notebook name for lesson_1 needs a slight adjustment if using the function directly,
# or we can create it explicitly as done below for clarity.
# For lesson_1_environment_setup, the notebook is lesson_1_notebook.ipynb
touch "lesson_1_environment_setup/lesson_1_notebook.ipynb" # Ensure correct notebook name

create_lesson "lesson_2_chatbot_basics"
touch "lesson_2_chatbot_basics/lesson_2_notebook.ipynb"

create_lesson "lesson_3_rag_web_access"
touch "lesson_3_rag_web_access/lesson_3_notebook.ipynb"

create_lesson "lesson_4_text_to_sql"
touch "lesson_4_text_to_sql/lesson_4_notebook.ipynb"
touch "lesson_4_text_to_sql/sample_database.sqlite"

create_lesson "lesson_5_document_rag"
touch "lesson_5_document_rag/lesson_5_notebook.ipynb"
mkdir -p "lesson_5_document_rag/sample_documents"

create_lesson "lesson_6_multilingual_agents"
touch "lesson_6_multilingual_agents/lesson_6_notebook.ipynb"

create_lesson "lesson_7_multi_agent_systems"
touch "lesson_7_multi_agent_systems/lesson_7_notebook.ipynb"

create_lesson "lesson_8_evaluation_metrics"
touch "lesson_8_evaluation_metrics/lesson_8_notebook.ipynb"
mkdir -p "lesson_8_evaluation_metrics/evaluation_datasets"

create_lesson "lesson_9_api_deployment"
touch "lesson_9_api_deployment/lesson_9_notebook.ipynb"
touch "lesson_9_api_deployment/app.py"

create_lesson "lesson_10_production"
touch "lesson_10_production/lesson_10_notebook.ipynb"
touch "lesson_10_production/Dockerfile"
touch "lesson_10_production/docker-compose.yml"

echo "Directory structure and files created successfully!"