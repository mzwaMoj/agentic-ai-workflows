"""
MLflow Custom Metrics for Text2SQL Evaluation
This module defines custom MLflow metrics specifically for Text2SQL systems
"""

import mlflow
from mlflow.metrics import make_metric, MetricValue
from typing import List, Dict, Any
import re


def sql_syntax_correctness(predictions, targets=None, metrics=None):
    """Custom MLflow metric for SQL syntax correctness"""
    correct = 0
    total = len(predictions)
    
    for pred in predictions:
        sql_query = pred.get('sql_query', '') if isinstance(pred, dict) else str(pred)
        if _validate_sql_basic_syntax(sql_query):
            correct += 1
    
    return MetricValue(scores=[correct / total if total > 0 else 0])


def routing_precision(predictions, targets=None, metrics=None):
    """Custom MLflow metric for query routing accuracy"""
    if not targets:
        return MetricValue(scores=[0])
    
    correct_routes = 0
    total = len(predictions)
    
    for pred, target in zip(predictions, targets):
        pred_routing = pred.get('routing_info', {}).get('requires_sql', False) if isinstance(pred, dict) else False
        target_routing = target.get('should_route_to_sql', True) if isinstance(target, dict) else bool(target)
        
        if pred_routing == target_routing:
            correct_routes += 1
    
    return MetricValue(scores=[correct_routes / total if total > 0 else 0])


def chart_generation_effectiveness(predictions, targets=None, metrics=None):
    """Custom MLflow metric for chart generation success"""
    chart_requests = 0
    successful_charts = 0
    
    for pred in predictions:
        if isinstance(pred, dict):
            query = pred.get('query', '')
            chart_html = pred.get('chart_html')
            
            # Check if chart was requested
            if _chart_requested_in_query(query):
                chart_requests += 1
                if chart_html and chart_html.strip():
                    successful_charts += 1
    
    return MetricValue(scores=[successful_charts / chart_requests if chart_requests > 0 else 1.0])


def response_completeness(predictions, targets=None, metrics=None):
    """Custom MLflow metric for response completeness"""
    complete_responses = 0
    total = len(predictions)
    
    for pred in predictions:
        if isinstance(pred, dict):
            response = pred.get('response', '')
            sql_results = pred.get('sql_results', [])
            success = pred.get('success', False)
            
            # A response is complete if it's successful and has content
            if success and response and len(response.strip()) > 10:
                complete_responses += 1
    
    return MetricValue(scores=[complete_responses / total if total > 0 else 0])


def safety_compliance_score(predictions, targets=None, metrics=None):
    """Custom MLflow metric for SQL safety compliance"""
    safe_queries = 0
    total = len(predictions)
    
    dangerous_operations = ['DELETE', 'UPDATE', 'INSERT', 'DROP', 'ALTER', 'TRUNCATE', 'CREATE']
    
    for pred in predictions:
        sql_query = pred.get('sql_query', '') if isinstance(pred, dict) else str(pred)
        sql_upper = sql_query.upper()
        
        if not any(op in sql_upper for op in dangerous_operations):
            safe_queries += 1
    
    return MetricValue(scores=[safe_queries / total if total > 0 else 0])


def multi_intent_success_rate(predictions, targets=None, metrics=None):
    """Custom MLflow metric for multi-intent query handling"""
    if not targets:
        return MetricValue(scores=[0])
    
    successful_multi_intent = 0
    multi_intent_queries = 0
    
    for pred, target in zip(predictions, targets):
        if isinstance(target, dict):
            required_components = target.get('required_components', [])
            
            # Only evaluate multi-intent queries
            if len(required_components) > 1:
                multi_intent_queries += 1
                
                # Check if all required components are present
                if isinstance(pred, dict):
                    has_data = bool(pred.get('sql_results'))
                    has_chart = bool(pred.get('chart_html'))
                    has_analysis = bool(pred.get('response'))
                    
                    components_present = []
                    if 'data' in required_components and has_data:
                        components_present.append('data')
                    if 'chart' in required_components and has_chart:
                        components_present.append('chart')
                    if 'analysis' in required_components and has_analysis:
                        components_present.append('analysis')
                    
                    if all(comp in components_present for comp in required_components):
                        successful_multi_intent += 1
    
    return MetricValue(scores=[successful_multi_intent / multi_intent_queries if multi_intent_queries > 0 else 1.0])


# Helper functions
def _validate_sql_basic_syntax(sql: str) -> bool:
    """Basic SQL syntax validation"""
    if not sql or sql.strip() == "":
        return False
    
    sql_upper = sql.upper().strip()
    
    # Must start with SELECT
    if not sql_upper.startswith('SELECT'):
        return False
    
    # Check for dangerous operations
    dangerous_ops = ['DELETE', 'UPDATE', 'INSERT', 'DROP', 'ALTER', 'TRUNCATE', 'CREATE']
    if any(op in sql_upper for op in dangerous_ops):
        return False
    
    # Basic structure check
    if 'FROM' not in sql_upper:
        return False
    
    return True


def _chart_requested_in_query(query: str) -> bool:
    """Check if query contains chart-related keywords"""
    chart_keywords = [
        'chart', 'graph', 'plot', 'visual', 'pie', 'bar', 'line', 'scatter',
        'histogram', 'heatmap', 'boxplot', 'distribution', 'visualization'
    ]
    return any(keyword in query.lower() for keyword in chart_keywords)


# Create MLflow metrics
text2sql_sql_syntax = make_metric(
    eval_fn=sql_syntax_correctness,
    greater_is_better=True,
    name="text2sql_sql_syntax_correctness"
)

text2sql_routing = make_metric(
    eval_fn=routing_precision,
    greater_is_better=True,
    name="text2sql_routing_precision"
)

text2sql_chart_generation = make_metric(
    eval_fn=chart_generation_effectiveness,
    greater_is_better=True,
    name="text2sql_chart_generation_effectiveness"
)

text2sql_completeness = make_metric(
    eval_fn=response_completeness,
    greater_is_better=True,
    name="text2sql_response_completeness"
)

text2sql_safety = make_metric(
    eval_fn=safety_compliance_score,
    greater_is_better=True,
    name="text2sql_safety_compliance"
)

text2sql_multi_intent = make_metric(
    eval_fn=multi_intent_success_rate,
    greater_is_better=True,
    name="text2sql_multi_intent_success"
)

# Metric collection for easy import
TEXT2SQL_METRICS = [
    text2sql_sql_syntax,
    text2sql_routing,
    text2sql_chart_generation,
    text2sql_completeness,
    text2sql_safety,
    text2sql_multi_intent
]
