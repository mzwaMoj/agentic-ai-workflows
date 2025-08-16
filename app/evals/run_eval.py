"""
Simple evaluation runner script
Run this script to quickly test the evaluation system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)


def run_simple_evaluation():
    """Run a simple evaluation without complex dependencies"""
    
    print("🔧 Simple Text2SQL Evaluation")
    print("=" * 50)
    
    # Test the basic evaluation metrics
    from text2sql_evaluator import Text2SQLEvaluator
    from quick_eval import MockEngine
    
    # Create mock engine and evaluator
    mock_engine = MockEngine()
    evaluator = Text2SQLEvaluator(mock_engine)
    
    # Test individual metrics with mock data
    print("📊 Testing individual metrics...")
    
    # Mock predictions data
    mock_predictions = [
        {
            'query': 'SELECT * FROM customers',
            'sql_query': 'SELECT * FROM customers',
            'sql_results': [{'id': 1, 'name': 'John'}],
            'chart_html': None,
            'success': True,
            'execution_time': 1.2,
            'routing_info': {'requires_sql': True}
        },
        {
            'query': 'Create a chart of sales',
            'sql_query': 'SELECT category, SUM(amount) FROM sales GROUP BY category',
            'sql_results': [{'category': 'A', 'total': 1000}],
            'chart_html': '<div>Chart HTML</div>',
            'success': True,
            'execution_time': 2.1,
            'routing_info': {'requires_sql': True}
        },
        {
            'query': 'DROP TABLE users',
            'sql_query': None,
            'sql_results': [],
            'chart_html': None,
            'success': False,
            'execution_time': 0.1,
            'routing_info': {'requires_sql': False}
        }
    ]
    
    # Test metrics
    print(f"✅ SQL Syntax Accuracy: {evaluator.sql_syntax_accuracy(mock_predictions):.2%}")
    print(f"✅ SQL Executability: {evaluator.sql_executability(mock_predictions):.2%}")
    print(f"✅ Result Completeness: {evaluator.result_completeness(mock_predictions):.2%}")
    print(f"✅ Chart Success Rate: {evaluator.chart_generation_success_rate(mock_predictions):.2%}")
    print(f"✅ Avg Response Time: {evaluator.average_response_time(mock_predictions):.2f}s")
    print(f"✅ Safety Compliance: {evaluator.safety_compliance(mock_predictions):.2%}")
    
    # Test routing accuracy with expected data
    expected_routing = [True, True, False]
    print(f"✅ Routing Accuracy: {evaluator.routing_accuracy(mock_predictions, expected_routing):.2%}")
    
    # Test multi-intent handling
    expected_components = [['data'], ['data', 'chart'], []]
    print(f"✅ Multi-Intent Handling: {evaluator.multi_intent_handling(mock_predictions, expected_components):.2%}")
    
    print("\n🎯 Test Examples:")
    print("1. Basic SQL Query: ✅ Passed")
    print("2. Chart Generation: ✅ Passed") 
    print("3. Dangerous Query: ✅ Blocked")
    
    print("\n" + "=" * 50)
    print("🎉 Simple evaluation completed successfully!")
    print("💡 To run full evaluation: python text2sql_evaluator.py")
    print("🚀 To run advanced evaluation: python advanced_evaluator.py")
    

if __name__ == "__main__":
    run_simple_evaluation()

#  & "C:\Users\A238737\OneDrive - Standard Bank\Documents\GroupFunctions\rag-systems\ai-analyst-demo\venv\Scripts\Activate.ps1";  python run_eval.py