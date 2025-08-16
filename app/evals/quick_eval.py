"""
Quick Text2SQL Evaluation Runner
Simple script to run basic evaluations on the Text2SQL system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from text2sql_evaluator import Text2SQLEvaluator, create_test_dataset


class MockEngine:
    """Mock engine for testing evaluation metrics without full system"""
    
    async def process_query(self, user_input: str, chat_history=None):
        """Mock query processing for testing"""
        import time
        import random
        
        start_time = time.time()
        
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Mock results based on query content
        if 'DROP' in user_input.upper() or 'DELETE' in user_input.upper():
            return {
                'success': False,
                'response': 'I cannot process dangerous SQL operations.',
                'sql_code': None,
                'sql_results': [],
                'chart_html': None,
                'routing_info': {'requires_sql': False}
            }
        
        if any(word in user_input.lower() for word in ['chart', 'graph', 'plot', 'visual']):
            return {
                'success': True,
                'response': 'Here is your data analysis with visualization.',
                'sql_code': f'SELECT * FROM customer_information WHERE balance > 10000',
                'sql_results': [{'id': 1, 'name': 'John Doe', 'balance': 25000}],
                'chart_html': '<div>Mock Chart HTML</div>',
                'routing_info': {'requires_sql': True}
            }
        
        if 'weather' in user_input.lower():
            return {
                'success': True,
                'response': 'I can only help with database queries, not weather information.',
                'sql_code': None,
                'sql_results': [],
                'chart_html': None,
                'routing_info': {'requires_sql': False}
            }
        
        # Default SQL query response
        return {
            'success': True,
            'response': 'Here are your query results.',
            'sql_code': f'SELECT * FROM customer_information LIMIT 10',
            'sql_results': [
                {'id': i, 'name': f'Customer {i}', 'balance': random.randint(1000, 50000)}
                for i in range(random.randint(1, 10))
            ],
            'chart_html': None,
            'routing_info': {'requires_sql': True}
        }


def run_quick_eval():
    """Run a quick evaluation with mock data"""
    print("🚀 Running Quick Text2SQL Evaluation...")
    print("📝 Using mock engine for testing evaluation metrics")
    
    # Create mock engine
    mock_engine = MockEngine()
    evaluator = Text2SQLEvaluator(mock_engine)
    
    # Create smaller test dataset for quick testing
    quick_test_data = [
        {
            'query': 'Show me all customers',
            'should_route_to_sql': True,
            'expected_row_range': (1, 10),
            'required_components': ['data'],
            'category': 'basic_sql'
        },
        {
            'query': 'Create a pie chart of account types',
            'should_route_to_sql': True,
            'expected_row_range': (1, 10),
            'required_components': ['data', 'chart'],
            'category': 'chart_requests'
        },
        {
            'query': 'Show top customers and create a bar chart',
            'should_route_to_sql': True,
            'expected_row_range': (1, 10),
            'required_components': ['data', 'chart'],
            'category': 'multi_intent'
        },
        {
            'query': 'DROP TABLE customers',
            'should_route_to_sql': False,
            'expected_row_range': (0, 0),
            'required_components': [],
            'category': 'edge_cases'
        },
        {
            'query': 'What is the weather today?',
            'should_route_to_sql': False,
            'expected_row_range': (0, 0),
            'required_components': [],
            'category': 'edge_cases'
        }
    ]
    
    # Run evaluation
    async def run_eval():
        metrics = await evaluator.run_evaluation(quick_test_data)
        
        print("\n" + "="*50)
        print("📊 QUICK EVALUATION RESULTS")
        print("="*50)
        
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, float) and metric_name != 'avg_response_time':
                print(f"{metric_name}: {metric_value:.2%}")
            else:
                print(f"{metric_name}: {metric_value}")
        
        print("="*50)
        print("✅ Quick evaluation complete!")
        return metrics
    
    return asyncio.run(run_eval())


if __name__ == "__main__":
    run_quick_eval()
