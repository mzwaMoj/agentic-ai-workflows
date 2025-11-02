"""
Comprehensive Text2SQL Evaluation Runner

This module runs comprehensive evaluations on the Text2SQL system including:
- Test case execution
- Guardrail validation
- Response quality assessment
- MLflow metric tracking
- Performance benchmarking
"""

import asyncio
import json
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    import mlflow
    import pandas as pd
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("⚠️  MLflow not available - metrics won't be logged")

from app.evals.test_cases import (
    ALL_TEST_CASES,
    EvalTestCase,
    QueryDifficulty,
    QueryType,
    get_test_cases_by_difficulty,
    get_security_tests
)
from app.evals.guardrails import SQLGuardrails, GuardrailResult

logger = logging.getLogger(__name__)


class EvaluationMetrics:
    """Calculate and store evaluation metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.test_results = []
    
    def calculate_sql_accuracy(self, results: List[Dict]) -> float:
        """Percentage of queries that generated valid SQL"""
        valid_sql = sum(1 for r in results if r.get('sql_generated', False))
        return (valid_sql / len(results)) * 100 if results else 0.0
    
    def calculate_execution_success_rate(self, results: List[Dict]) -> float:
        """Percentage of queries that executed successfully"""
        successful = sum(1 for r in results if r.get('execution_success', False))
        return (successful / len(results)) * 100 if results else 0.0
    
    def calculate_guardrail_pass_rate(self, results: List[Dict]) -> float:
        """Percentage of queries that passed guardrails"""
        passed = sum(1 for r in results if r.get('guardrail_passed', False))
        return (passed / len(results)) * 100 if results else 0.0
    
    def calculate_security_block_rate(self, results: List[Dict]) -> float:
        """Percentage of unsafe queries that were blocked"""
        unsafe_queries = [r for r in results if not r.get('test_case', {}).get('security_safe', True)]
        if not unsafe_queries:
            return 100.0
        
        blocked = sum(1 for r in unsafe_queries if not r.get('guardrail_passed', True))
        return (blocked / len(unsafe_queries)) * 100
    
    def calculate_avg_latency(self, results: List[Dict]) -> float:
        """Average query execution time in seconds"""
        latencies = [r.get('latency', 0) for r in results if r.get('latency')]
        return sum(latencies) / len(latencies) if latencies else 0.0
    
    def calculate_chart_success_rate(self, results: List[Dict]) -> float:
        """Percentage of chart requests that succeeded"""
        chart_requests = [r for r in results if r.get('test_case', {}).get('requires_chart', False)]
        if not chart_requests:
            return 100.0
        
        successful = sum(1 for r in chart_requests if r.get('chart_generated', False))
        return (successful / len(chart_requests)) * 100
    
    def calculate_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate all metrics"""
        self.test_results = results
        
        self.metrics = {
            'sql_accuracy': self.calculate_sql_accuracy(results),
            'execution_success_rate': self.calculate_execution_success_rate(results),
            'guardrail_pass_rate': self.calculate_guardrail_pass_rate(results),
            'security_block_rate': self.calculate_security_block_rate(results),
            'avg_latency': self.calculate_avg_latency(results),
            'chart_success_rate': self.calculate_chart_success_rate(results),
            'total_tests': len(results),
            'total_passed': sum(1 for r in results if r.get('overall_success', False)),
        }
        
        self.metrics['overall_pass_rate'] = (
            self.metrics['total_passed'] / self.metrics['total_tests'] * 100
            if self.metrics['total_tests'] > 0 else 0.0
        )
        
        return self.metrics
    
    def get_metrics_by_difficulty(self, results: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Get metrics broken down by difficulty"""
        difficulty_metrics = {}
        
        for difficulty in QueryDifficulty:
            difficulty_results = [
                r for r in results
                if r.get('test_case', {}).get('difficulty') == difficulty.value
            ]
            
            if difficulty_results:
                difficulty_metrics[difficulty.value] = {
                    'count': len(difficulty_results),
                    'success_rate': (
                        sum(1 for r in difficulty_results if r.get('overall_success', False))
                        / len(difficulty_results) * 100
                    ),
                    'avg_latency': self.calculate_avg_latency(difficulty_results)
                }
        
        return difficulty_metrics


class Text2SQLEvaluationRunner:
    """Main evaluation runner"""
    
    def __init__(self, engine=None, config: Optional[Dict] = None):
        """
        Initialize evaluation runner
        
        Args:
            engine: Text2SQLEngine instance (optional for guardrail-only testing)
            config: Configuration dictionary
        """
        self.engine = engine
        self.config = config or {}
        self.guardrails = SQLGuardrails()
        self.metrics_calculator = EvaluationMetrics()
        self.results = []
    
    async def run_single_test(self, test_case: EvalTestCase) -> Dict[str, Any]:
        """
        Run a single test case
        
        Args:
            test_case: EvalTestCase to run
            
        Returns:
            Dictionary with test results
        """
        result = {
            'test_id': test_case.id,
            'test_case': {
                'query': test_case.query,
                'difficulty': test_case.difficulty.value,
                'query_type': test_case.query_type.value,
                'requires_sql': test_case.requires_sql,
                'requires_chart': test_case.requires_chart,
                'security_safe': test_case.security_safe,
                'should_succeed': test_case.should_succeed,
            },
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        start_time = time.time()
        
        try:
            # Step 1: Guardrail validation
            guardrail_result = self.guardrails.validate_query(test_case.query)
            result['guardrail_passed'] = guardrail_result.is_safe
            result['guardrail_violations'] = [
                {
                    'type': v.violation_type.value,
                    'risk_level': v.risk_level.value,
                    'message': v.message
                }
                for v in guardrail_result.violations
            ]
            result['guardrail_warnings'] = [
                {
                    'type': w.violation_type.value,
                    'message': w.message
                }
                for w in guardrail_result.warnings
            ]
            
            # Step 2: Execute query if engine available and guardrails pass
            if self.engine and (guardrail_result.is_safe or test_case.security_safe):
                try:
                    response = await self.engine.process_query(test_case.query)
                    
                    result['sql_generated'] = bool(response.get('sql_code'))
                    result['sql_code'] = response.get('sql_code', '')
                    result['execution_success'] = response.get('success', False)
                    result['response'] = response.get('response', '')
                    result['chart_generated'] = bool(response.get('chart_html'))
                    
                    # Check SQL results
                    sql_results = response.get('sql_results', [])
                    if sql_results:
                        result['rows_returned'] = len(sql_results)
                        result['results_in_range'] = (
                            test_case.expected_min_rows <= len(sql_results) <= test_case.expected_max_rows
                        )
                    else:
                        result['rows_returned'] = 0
                        result['results_in_range'] = test_case.expected_min_rows == 0
                    
                except Exception as e:
                    result['execution_success'] = False
                    result['error'] = str(e)
                    logger.error(f"Error executing test {test_case.id}: {e}")
            else:
                result['sql_generated'] = False
                result['execution_success'] = False
                result['skipped'] = True
                result['skip_reason'] = 'No engine available' if not self.engine else 'Guardrail blocked'
            
            # Calculate overall success
            result['overall_success'] = self._determine_overall_success(test_case, result)
            
        except Exception as e:
            result['overall_success'] = False
            result['error'] = str(e)
            logger.error(f"Error in test {test_case.id}: {e}")
        
        finally:
            result['latency'] = time.time() - start_time
        
        return result
    
    def _determine_overall_success(self, test_case: EvalTestCase, result: Dict) -> bool:
        """Determine if test passed overall"""
        # Security tests should be blocked
        if not test_case.security_safe:
            return not result.get('guardrail_passed', False)
        
        # Normal tests should pass guardrails and execute if expected to succeed
        if test_case.should_succeed:
            return (
                result.get('guardrail_passed', False) and
                result.get('execution_success', False) and
                result.get('results_in_range', False)
            )
        else:
            # Tests expected to fail should fail gracefully
            return not result.get('execution_success', True)
    
    async def run_evaluation(
        self,
        test_cases: Optional[List[EvalTestCase]] = None,
        filter_difficulty: Optional[QueryDifficulty] = None,
        filter_type: Optional[QueryType] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive evaluation
        
        Args:
            test_cases: List of test cases (uses ALL_TEST_CASES if None)
            filter_difficulty: Filter by difficulty level
            filter_type: Filter by query type
            
        Returns:
            Evaluation results dictionary
        """
        # Determine which test cases to run
        cases_to_run = test_cases or ALL_TEST_CASES
        
        if filter_difficulty:
            cases_to_run = [tc for tc in cases_to_run if tc.difficulty == filter_difficulty]
        
        if filter_type:
            cases_to_run = [tc for tc in cases_to_run if tc.query_type == filter_type]
        
        print(f"\n🧪 Running evaluation with {len(cases_to_run)} test cases...")
        print(f"{'='*60}\n")
        
        # Run all test cases
        results = []
        for i, test_case in enumerate(cases_to_run, 1):
            print(f"[{i}/{len(cases_to_run)}] Testing: {test_case.id} - {test_case.description[:50]}...")
            result = await self.run_single_test(test_case)
            results.append(result)
            
            # Print status
            status = "✅" if result['overall_success'] else "❌"
            print(f"    {status} {'PASS' if result['overall_success'] else 'FAIL'} (Latency: {result['latency']:.2f}s)")
        
        self.results = results
        
        # Calculate metrics
        metrics = self.metrics_calculator.calculate_metrics(results)
        difficulty_metrics = self.metrics_calculator.get_metrics_by_difficulty(results)
        
        evaluation_summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': len(results),
            'metrics': metrics,
            'difficulty_breakdown': difficulty_metrics,
            'results': results
        }
        
        return evaluation_summary
    
    def save_results(self, filepath: str = "evaluation_results.json"):
        """Save results to JSON file"""
        if not self.results:
            print("⚠️  No results to save")
            return
        
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': len(self.results),
            'metrics': self.metrics_calculator.metrics,
            'results': self.results
        }
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"✅ Saved results to {filepath}")
    
    def print_summary(self):
        """Print evaluation summary"""
        if not self.results:
            print("⚠️  No results available")
            return
        
        metrics = self.metrics_calculator.metrics
        
        print("\n" + "=" * 60)
        print("📊 EVALUATION SUMMARY")
        print("=" * 60)
        print(f"\n📈 Overall Metrics:")
        print(f"   Total Tests: {metrics['total_tests']}")
        print(f"   Passed: {metrics['total_passed']} ({metrics['overall_pass_rate']:.1f}%)")
        print(f"   SQL Accuracy: {metrics['sql_accuracy']:.1f}%")
        print(f"   Execution Success Rate: {metrics['execution_success_rate']:.1f}%")
        print(f"   Guardrail Pass Rate: {metrics['guardrail_pass_rate']:.1f}%")
        print(f"   Security Block Rate: {metrics['security_block_rate']:.1f}%")
        print(f"   Chart Success Rate: {metrics['chart_success_rate']:.1f}%")
        print(f"   Average Latency: {metrics['avg_latency']:.2f}s")
        
        # Difficulty breakdown
        difficulty_metrics = self.metrics_calculator.get_metrics_by_difficulty(self.results)
        if difficulty_metrics:
            print(f"\n📊 Performance by Difficulty:")
            for difficulty, metrics in difficulty_metrics.items():
                print(f"   {difficulty.title()}: {metrics['success_rate']:.1f}% ({metrics['count']} tests)")
        
        # Failed tests
        failed = [r for r in self.results if not r['overall_success']]
        if failed:
            print(f"\n❌ Failed Tests ({len(failed)}):")
            for r in failed[:5]:  # Show first 5
                print(f"   • {r['test_id']}: {r['test_case']['query'][:50]}...")
                if 'error' in r:
                    print(f"     Error: {r['error']}")
        
        print("\n" + "=" * 60)


async def main():
    """Main evaluation function"""
    print("\n🚀 Text2SQL Comprehensive Evaluation")
    print("=" * 60)
    
    # Option 1: Guardrail-only testing (no engine required)
    print("\n🔒 Running Guardrail-Only Evaluation...")
    runner = Text2SQLEvaluationRunner(engine=None)
    
    # Test security cases
    security_tests = get_security_tests()
    results = await runner.run_evaluation(test_cases=security_tests)
    
    runner.print_summary()
    runner.save_results("guardrail_eval_results.json")
    
    print("\n✅ Evaluation complete!")
    print("\nℹ️  To run full evaluation with SQL execution:")
    print("   1. Initialize your Text2SQLEngine")
    print("   2. Pass it to Text2SQLEvaluationRunner(engine=your_engine)")
    print("   3. Run runner.run_evaluation()")


if __name__ == "__main__":
    asyncio.run(main())
