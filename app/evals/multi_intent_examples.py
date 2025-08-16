"""
Multi-Intent Query Examples and Demonstration
This script showcases how the Text2SQL system handles complex queries with multiple intents
"""

import asyncio
import json
from typing import Dict, List


class MultiIntentQueryExamples:
    """Collection of multi-intent query examples for Text2SQL evaluation"""
    
    @staticmethod
    def get_multi_intent_examples() -> List[Dict]:
        """
        Returns a comprehensive set of multi-intent query examples
        Each query demonstrates handling multiple requirements in a single request
        """
        
        examples = [
            # ===== DATA + CHART COMBINATIONS =====
            {
                'query': 'Show me the top 10 customers by account balance and create a bar chart of their income distribution',
                'intents': ['data_retrieval', 'chart_generation'],
                'expected_operations': [
                    'Query customer data ordered by balance',
                    'Generate bar chart showing income categories'
                ],
                'required_components': ['data', 'chart'],
                'expected_sql_pattern': 'SELECT TOP 10.*balance.*ORDER BY.*DESC',
                'expected_chart_type': 'bar',
                'complexity': 'medium',
                'description': 'Combines customer ranking with income visualization'
            },
            
            {
                'query': 'Get all customers with loans over 50000 and visualize their credit scores in a histogram',
                'intents': ['data_filtering', 'chart_generation'],
                'expected_operations': [
                    'Filter customers by loan amount > 50000',
                    'Create histogram of credit score distribution'
                ],
                'required_components': ['data', 'chart'],
                'expected_sql_pattern': 'SELECT.*WHERE.*loan.*> 50000',
                'expected_chart_type': 'histogram',
                'complexity': 'medium',
                'description': 'Filters loan data and shows credit score distribution'
            },
            
            {
                'query': 'Find transaction data for the last 6 months and show spending patterns by category in a pie chart',
                'intents': ['temporal_analysis', 'categorical_analysis', 'chart_generation'],
                'expected_operations': [
                    'Filter transactions by date (last 6 months)',
                    'Group spending by category',
                    'Generate pie chart of category distribution'
                ],
                'required_components': ['data', 'chart', 'analysis'],
                'expected_sql_pattern': 'SELECT.*category.*SUM.*WHERE.*date.*GROUP BY',
                'expected_chart_type': 'pie',
                'complexity': 'high',
                'description': 'Time-based filtering with categorical analysis and visualization'
            },
            
            # ===== COMPARATIVE ANALYSIS + VISUALIZATION =====
            {
                'query': 'Compare loan eligibility rates across different income categories and show the results in both a table and a pie chart',
                'intents': ['comparative_analysis', 'table_generation', 'chart_generation'],
                'expected_operations': [
                    'Calculate loan eligibility by income category',
                    'Present results in tabular format',
                    'Create pie chart showing eligibility distribution'
                ],
                'required_components': ['data', 'chart', 'analysis'],
                'expected_sql_pattern': 'SELECT.*income_category.*loan_eligible.*GROUP BY',
                'expected_chart_type': 'pie',
                'complexity': 'high',
                'description': 'Multi-format output with comparative analysis'
            },
            
            {
                'query': 'Analyze customer demographics by age groups and create a stacked bar chart showing gender distribution within each age group',
                'intents': ['demographic_analysis', 'grouping', 'chart_generation'],
                'expected_operations': [
                    'Group customers by age ranges',
                    'Calculate gender distribution per age group',
                    'Generate stacked bar chart'
                ],
                'required_components': ['data', 'chart', 'analysis'],
                'expected_sql_pattern': 'SELECT.*age.*gender.*GROUP BY',
                'expected_chart_type': 'stacked_bar',
                'complexity': 'high',
                'description': 'Demographic segmentation with nested categorization'
            },
            
            # ===== TREND ANALYSIS + FORECASTING =====
            {
                'query': 'Show quarterly transaction trends for the past 2 years and predict the next quarter using a line chart with trend analysis',
                'intents': ['temporal_analysis', 'trend_analysis', 'forecasting', 'chart_generation'],
                'expected_operations': [
                    'Group transactions by quarter',
                    'Calculate quarterly totals',
                    'Identify trends and patterns',
                    'Generate line chart with trend line'
                ],
                'required_components': ['data', 'chart', 'analysis'],
                'expected_sql_pattern': 'SELECT.*DATEPART.*quarter.*SUM.*GROUP BY',
                'expected_chart_type': 'line',
                'complexity': 'very_high',
                'description': 'Time series analysis with predictive elements'
            },
            
            # ===== MULTI-TABLE ANALYSIS =====
            {
                'query': 'Analyze the relationship between customer balances and their transaction frequencies, then show correlations in a scatter plot',
                'intents': ['relationship_analysis', 'statistical_analysis', 'chart_generation'],
                'expected_operations': [
                    'Join customer and transaction data',
                    'Calculate transaction frequency per customer',
                    'Analyze balance vs frequency correlation',
                    'Generate scatter plot'
                ],
                'required_components': ['data', 'chart', 'analysis'],
                'expected_sql_pattern': 'SELECT.*COUNT.*GROUP BY.*customer',
                'expected_chart_type': 'scatter',
                'complexity': 'high',
                'description': 'Cross-table correlation analysis with visualization'
            },
            
            # ===== BUSINESS INTELLIGENCE QUERIES =====
            {
                'query': 'Create a comprehensive dashboard showing: 1) Top 5 most profitable customer segments, 2) Monthly revenue trends, 3) Product adoption rates by age group - include both tables and charts',
                'intents': ['segmentation_analysis', 'trend_analysis', 'adoption_analysis', 'dashboard_creation'],
                'expected_operations': [
                    'Identify profitable customer segments',
                    'Calculate monthly revenue trends',
                    'Analyze product adoption by age',
                    'Generate multiple visualizations'
                ],
                'required_components': ['data', 'chart', 'analysis'],
                'expected_sql_pattern': 'Multiple queries for different analyses',
                'expected_chart_type': 'multiple',
                'complexity': 'very_high',
                'description': 'Multi-faceted business intelligence analysis'
            },
            
            # ===== RISK ANALYSIS + REPORTING =====
            {
                'query': 'Identify high-risk customers based on loan default probability, segment them by risk levels, and create a risk assessment report with visual indicators',
                'intents': ['risk_analysis', 'segmentation', 'scoring', 'report_generation'],
                'expected_operations': [
                    'Calculate risk scores for customers',
                    'Segment customers by risk levels',
                    'Generate risk assessment metrics',
                    'Create visual risk indicators'
                ],
                'required_components': ['data', 'chart', 'analysis'],
                'expected_sql_pattern': 'SELECT.*credit_score.*loan.*CASE WHEN',
                'expected_chart_type': 'heatmap',
                'complexity': 'very_high',
                'description': 'Complex risk modeling with multiple outputs'
            }
        ]
        
        return examples
    
    @staticmethod
    def get_intent_categories():
        """Returns definitions of different intent categories"""
        return {
            'data_retrieval': 'Fetching specific data from database tables',
            'data_filtering': 'Applying WHERE conditions to filter results',
            'chart_generation': 'Creating visual representations of data',
            'temporal_analysis': 'Time-based data analysis and filtering',
            'categorical_analysis': 'Grouping and analyzing by categories',
            'comparative_analysis': 'Comparing different groups or segments',
            'trend_analysis': 'Identifying patterns and trends over time',
            'demographic_analysis': 'Analyzing customer demographic data',
            'relationship_analysis': 'Finding correlations between variables',
            'statistical_analysis': 'Calculating statistical measures',
            'segmentation': 'Dividing data into meaningful groups',
            'forecasting': 'Predicting future values based on trends',
            'risk_analysis': 'Assessing and calculating risk factors',
            'business_intelligence': 'Comprehensive business analysis',
            'dashboard_creation': 'Creating multi-component dashboards',
            'report_generation': 'Generating formatted reports'
        }
    
    @staticmethod
    def demonstrate_multi_intent_processing():
        """Demonstrates how multi-intent queries should be processed"""
        
        print("🎯 Multi-Intent Query Processing Demonstration")
        print("=" * 60)
        
        examples = MultiIntentQueryExamples.get_multi_intent_examples()
        intent_categories = MultiIntentQueryExamples.get_intent_categories()
        
        for i, example in enumerate(examples[:3], 1):  # Show first 3 examples
            print(f"\n📝 Example {i}: {example['complexity'].upper()} Complexity")
            print("-" * 40)
            print(f"Query: {example['query']}")
            print(f"\nIntents Identified:")
            for intent in example['intents']:
                print(f"  • {intent}: {intent_categories.get(intent, 'Unknown intent')}")
            
            print(f"\nExpected Operations:")
            for j, operation in enumerate(example['expected_operations'], 1):
                print(f"  {j}. {operation}")
            
            print(f"\nRequired Components: {', '.join(example['required_components'])}")
            print(f"Expected Chart Type: {example.get('expected_chart_type', 'N/A')}")
            print(f"Description: {example['description']}")
        
        print("\n" + "=" * 60)
        print("💡 Key Points for Multi-Intent Processing:")
        print("  1. Parse query to identify all intent types")
        print("  2. Plan execution order (data first, then analysis, then visualization)")
        print("  3. Ensure all required components are generated")
        print("  4. Validate that outputs satisfy all identified intents")
        print("  5. Provide comprehensive response addressing all aspects")


def create_multi_intent_test_suite():
    """Creates a comprehensive test suite for multi-intent evaluation"""
    
    examples = MultiIntentQueryExamples.get_multi_intent_examples()
    
    test_suite = []
    for example in examples:
        test_case = {
            'query': example['query'],
            'should_route_to_sql': True,
            'expected_row_range': (1, 100),  # Flexible range for multi-intent
            'required_components': example['required_components'],
            'category': 'multi_intent',
            'complexity': example['complexity'],
            'expected_intents': example['intents'],
            'expected_chart_type': example.get('expected_chart_type'),
            'description': example['description']
        }
        test_suite.append(test_case)
    
    return test_suite


def analyze_multi_intent_complexity():
    """Analyzes the complexity distribution of multi-intent queries"""
    
    examples = MultiIntentQueryExamples.get_multi_intent_examples()
    
    complexity_counts = {}
    intent_counts = {}
    
    for example in examples:
        # Count complexity levels
        complexity = example['complexity']
        complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
        
        # Count intent combinations
        intent_count = len(example['intents'])
        intent_counts[intent_count] = intent_counts.get(intent_count, 0) + 1
    
    print("📊 Multi-Intent Query Analysis")
    print("=" * 40)
    
    print("\n🎯 Complexity Distribution:")
    for complexity, count in sorted(complexity_counts.items()):
        print(f"  • {complexity.replace('_', ' ').title()}: {count} queries")
    
    print("\n🔗 Intent Count Distribution:")
    for intent_count, count in sorted(intent_counts.items()):
        print(f"  • {intent_count} intents: {count} queries")
    
    print(f"\n📈 Total Multi-Intent Examples: {len(examples)}")
    print(f"📊 Average Intents per Query: {sum(len(ex['intents']) for ex in examples) / len(examples):.1f}")


if __name__ == "__main__":
    print("🚀 Multi-Intent Query Examples for Text2SQL Evaluation\n")
    
    # Demonstrate multi-intent processing
    MultiIntentQueryExamples.demonstrate_multi_intent_processing()
    
    print("\n")
    
    # Analyze complexity
    analyze_multi_intent_complexity()
    
    print("\n🎯 Use these examples in your evaluation:")
    print("  • Copy examples into your test dataset")
    print("  • Modify complexity levels as needed")
    print("  • Add domain-specific examples")
    print("  • Test incremental complexity progression")
    
    # Save examples to JSON for easy import
    examples = MultiIntentQueryExamples.get_multi_intent_examples()
    with open('multi_intent_examples.json', 'w', encoding='utf-8') as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Examples saved to: multi_intent_examples.json")
