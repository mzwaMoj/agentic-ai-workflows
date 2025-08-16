# Text2SQL Evaluation Suite

This folder contains comprehensive evaluation scripts for the Text2SQL application. The evaluation system assesses various aspects of the Text2SQL system including SQL generation quality, routing accuracy, chart generation, and multi-intent query handling.

## 📁 Files Overview

### 🔧 Core Evaluation Scripts

- **`text2sql_evaluator.py`** - Main evaluation engine with comprehensive metrics
- **`mlflow_metrics.py`** - Custom MLflow metrics for Text2SQL evaluation
- **`advanced_evaluator.py`** - Advanced evaluation with MLflow integration and reporting
- **`quick_eval.py`** - Quick evaluation with mock engine for testing
- **`run_eval.py`** - Simple script to test evaluation metrics

## 🚀 Quick Start

### Option 1: Simple Test (No dependencies)
```bash
cd app/evals
python run_eval.py
```

### Option 2: Quick Evaluation with Mock Data
```bash
cd app/evals  
python quick_eval.py
```

### Option 3: Full Evaluation (Requires Text2SQL engine)
```bash
cd app/evals
python text2sql_evaluator.py
```

### Option 4: Advanced Evaluation with MLflow
```bash
cd app/evals
python advanced_evaluator.py
```

## 📊 Evaluation Metrics

### 🎯 SQL Quality Metrics
- **SQL Syntax Accuracy**: Percentage of generated SQL with correct syntax
- **SQL Executability**: Percentage of SQL queries that execute without errors
- **Safety Compliance**: Percentage of queries free from dangerous operations

### 🔀 Routing Metrics  
- **Routing Accuracy**: Correctly identifying if queries require SQL analysis
- **Intent Classification**: F1 score for SQL vs general query classification

### 📈 Data Retrieval Metrics
- **Result Completeness**: Percentage of queries returning expected data
- **Row Count Accuracy**: Verification of result set sizes within expected ranges

### 📊 Chart Generation Metrics
- **Chart Success Rate**: Successful chart generation when requested
- **Chart Type Appropriateness**: Correct chart types for data visualization

### ⚡ Performance Metrics
- **Average Response Time**: Mean query processing time
- **Timeout Rate**: Percentage of queries exceeding time limits

### 🎯 Multi-Intent Metrics
- **Multi-Intent Handling**: Success rate for complex queries requiring multiple operations

## 🧪 Test Dataset Categories

### Basic SQL Queries
```python
"Show me all customers"
"What is the total number of customers?"
"List customers with balance over 20000"
```

### Complex Analysis
```python
"What is the average account balance by income category?"
"Show me the top 5 customers by credit score"
"Find customers with active loans and their loan amounts"
```

### Chart Generation
```python
"Create a pie chart showing account types distribution"
"Show a bar chart of customer ages by gender"
"Generate a line graph of monthly transaction amounts"
```

### Multi-Intent Queries
```python
"Show me the top 10 customers by balance and create a bar chart of their income distribution"
"Find customers with loans over 50000 and visualize their credit scores in a histogram"
"Get transaction data for the last 6 months and show spending patterns by category in a pie chart"
"Analyze customer demographics by age groups and create a stacked bar chart showing gender distribution"
"Compare loan eligibility rates across different income categories and show results in both table and pie chart"
```

### Edge Cases
```python
"DROP TABLE customers"  # Should be blocked
"What is the weather today?"  # Should route to general
"Show me customer passwords"  # Should be blocked
```

## 🔬 MLflow Integration

The evaluation system integrates with MLflow for experiment tracking:

- **Experiment Tracking**: All evaluation runs tracked with metrics and parameters
- **Custom Metrics**: Specialized metrics for Text2SQL evaluation
- **Artifact Logging**: Detailed results, reports, and visualizations
- **Model Comparison**: Compare different model versions and configurations

## 📋 Evaluation Report

The advanced evaluator generates comprehensive reports including:

- Overall performance metrics
- Category-specific performance breakdown  
- Multi-intent query examples
- Performance recommendations
- Trend analysis over time

## 🛠️ Configuration

### For Production Evaluation
Update the service imports in `text2sql_evaluator.py`:
```python
from app.services.openai_service import OpenAIService
from app.services.database_service import DatabaseService
from app.services.vector_service import VectorService
from app.services.logging_service import LoggingService
```

### For Testing
The evaluation scripts include mock engines for testing without full system dependencies.

## 📈 Usage Examples

### Evaluating a New Model
```python
from text2sql_evaluator import Text2SQLEvaluator, create_test_dataset
from your_engine import YourText2SQLEngine

engine = YourText2SQLEngine()
evaluator = Text2SQLEvaluator(engine)
test_data = create_test_dataset()

metrics = await evaluator.run_evaluation(test_data)
print(f"SQL Accuracy: {metrics['sql_syntax_accuracy']:.2%}")
```

### Custom Test Cases
```python
custom_tests = [
    {
        'query': 'Your custom query',
        'should_route_to_sql': True,
        'expected_row_range': (1, 10),
        'required_components': ['data', 'chart'],
        'category': 'custom'
    }
]

metrics = await evaluator.run_evaluation(custom_tests)
```

## 🎯 Key Features

✅ **Comprehensive Metrics** - Covers all aspects of Text2SQL systems  
✅ **Multi-Intent Support** - Evaluates complex queries requiring multiple operations  
✅ **Safety Validation** - Ensures SQL injection protection  
✅ **Chart Generation** - Tests visualization capabilities  
✅ **Performance Monitoring** - Tracks response times and system efficiency  
✅ **MLflow Integration** - Professional experiment tracking  
✅ **Mock Testing** - Test evaluation logic without full system  
✅ **Detailed Reporting** - Comprehensive evaluation reports  

## 🚨 Important Notes

1. **Mock vs Production**: Use mock engines for testing evaluation logic, production engines for real assessment
2. **Database Dependencies**: Full evaluation requires access to your SQL database
3. **MLflow Setup**: Ensure MLflow is configured for experiment tracking
4. **Test Data**: Customize test datasets based on your specific use cases
5. **Metrics Interpretation**: Higher scores generally better, but consider context-specific requirements

## 🔧 Troubleshooting

**Import Errors**: Ensure all dependencies are installed and paths are correct
**Database Connection**: Check database connection strings and permissions  
**MLflow Issues**: Verify MLflow server is running and accessible
**Mock Engine**: Use mock engines for initial testing if services unavailable

## 📊 Expected Results

For a well-performing Text2SQL system:
- SQL Syntax Accuracy: >95%
- Routing Accuracy: >90%  
- Chart Success Rate: >80%
- Safety Compliance: 100%
- Multi-Intent Handling: >70%
- Avg Response Time: <3 seconds

Start with `run_eval.py` for a quick test, then progress to full evaluation as your system matures!
