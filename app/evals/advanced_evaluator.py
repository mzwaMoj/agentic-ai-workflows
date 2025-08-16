"""
Advanced Text2SQL Evaluation with MLflow Integration
This script demonstrates advanced evaluation techniques with MLflow tracking
"""

import asyncio
import mlflow
import pandas as pd
from datetime import datetime
import sys
import os
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from text2sql_evaluator import Text2SQLEvaluator, create_test_dataset
from mlflow_metrics import TEXT2SQL_METRICS


class AdvancedText2SQLEvaluator:
    """Advanced evaluator with MLflow integration"""
    
    def __init__(self, engine=None):
        self.engine = engine
        
    async def run_comprehensive_evaluation(self):
        """Run comprehensive evaluation with MLflow tracking"""
        
        print("🚀 Starting Advanced Text2SQL Evaluation with MLflow...")
        
        # Set MLflow experiment
        experiment_name = "text2sql_comprehensive_evaluation"
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name=f"advanced_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            
            # Create test dataset
            test_data = create_test_dataset()
            
            # If no engine provided, use mock engine for demonstration
            if not self.engine:
                from quick_eval import MockEngine
                self.engine = MockEngine()
                mlflow.log_param("engine_type", "mock")
            else:
                mlflow.log_param("engine_type", "production")
            
            # Log experiment parameters
            mlflow.log_param("total_test_cases", len(test_data))
            mlflow.log_param("evaluation_timestamp", datetime.now().isoformat())
            
            # Group test cases by category
            categories = {}
            for test_case in test_data:
                category = test_case.get('category', 'unknown')
                if category not in categories:
                    categories[category] = []
                categories[category].append(test_case)
            
            mlflow.log_param("test_categories", list(categories.keys()))
            for cat, cases in categories.items():
                mlflow.log_param(f"category_{cat}_count", len(cases))
            
            # Run evaluation
            evaluator = Text2SQLEvaluator(self.engine)
            overall_metrics = await evaluator.run_evaluation(test_data)
            
            # Log overall metrics
            for metric_name, metric_value in overall_metrics.items():
                mlflow.log_metric(f"overall_{metric_name}", metric_value)
            
            # Evaluate by category
            print("\n📊 Running category-specific evaluations...")
            category_results = {}
            
            for category, cases in categories.items():
                print(f"  Evaluating {category}: {len(cases)} cases")
                
                category_evaluator = Text2SQLEvaluator(self.engine)
                category_metrics = await category_evaluator.run_evaluation(cases)
                category_results[category] = category_metrics
                
                # Log category metrics
                for metric_name, metric_value in category_metrics.items():
                    mlflow.log_metric(f"{category}_{metric_name}", metric_value)
            
            # Create evaluation report
            await self._create_evaluation_report(overall_metrics, category_results, test_data)
            
            # Use MLflow's built-in evaluation (if available)
            await self._run_mlflow_native_evaluation(test_data, evaluator.results)
            
            print(f"\n✅ Advanced evaluation complete!")
            print(f"🔬 MLflow run ID: {mlflow.active_run().info.run_id}")
            
            return overall_metrics, category_results
    
    async def _create_evaluation_report(self, overall_metrics, category_results, test_data):
        """Create detailed evaluation report"""
        
        print("📝 Creating evaluation report...")
        
        report = []
        report.append("# Text2SQL System Evaluation Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Overall metrics
        report.append("## Overall Performance")
        report.append("| Metric | Score |")
        report.append("|--------|-------|")
        
        key_metrics = [
            'sql_syntax_accuracy', 'sql_executability', 'routing_accuracy',
            'chart_success_rate', 'safety_compliance', 'multi_intent_handling'
        ]
        
        for metric in key_metrics:
            if metric in overall_metrics:
                score = overall_metrics[metric]
                if isinstance(score, float):
                    report.append(f"| {metric.replace('_', ' ').title()} | {score:.2%} |")
                else:
                    report.append(f"| {metric.replace('_', ' ').title()} | {score} |")
        
        report.append("")
        
        # Category breakdown
        report.append("## Performance by Category")
        for category, metrics in category_results.items():
            report.append(f"### {category.replace('_', ' ').title()}")
            report.append("| Metric | Score |")
            report.append("|--------|-------|")
            
            for metric in key_metrics:
                if metric in metrics:
                    score = metrics[metric]
                    if isinstance(score, float):
                        report.append(f"| {metric.replace('_', ' ').title()} | {score:.2%} |")
                    else:
                        report.append(f"| {metric.replace('_', ' ').title()} | {score} |")
            report.append("")
        
        # Multi-intent examples
        report.append("## Multi-Intent Query Examples")
        multi_intent_cases = [case for case in test_data if case.get('category') == 'multi_intent']
        for i, case in enumerate(multi_intent_cases[:3], 1):
            report.append(f"{i}. **Query**: {case['query']}")
            report.append(f"   **Required Components**: {', '.join(case['required_components'])}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        
        if overall_metrics.get('sql_syntax_accuracy', 0) < 0.9:
            report.append("- ⚠️ SQL syntax accuracy below 90%. Review SQL generation prompts.")
        
        if overall_metrics.get('chart_success_rate', 0) < 0.8:
            report.append("- ⚠️ Chart generation success rate below 80%. Check chart generation logic.")
        
        if overall_metrics.get('multi_intent_handling', 0) < 0.7:
            report.append("- ⚠️ Multi-intent handling below 70%. Improve query parsing for complex requests.")
        
        if overall_metrics.get('safety_compliance', 0) < 1.0:
            report.append("- ⚠️ Safety compliance not 100%. Review SQL validation rules.")
        
        report.append("")
        report.append("---")
        report.append("*Report generated by Text2SQL Advanced Evaluator*")
        
        # Save report
        report_content = "\n".join(report)
        report_file = f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        mlflow.log_artifact(report_file)
        print(f"📄 Report saved: {report_file}")
    
    async def _run_mlflow_native_evaluation(self, test_data, predictions):
        """Run MLflow's native evaluation if supported"""
        
        try:
            print("🔬 Running MLflow native evaluation...")
            
            # Prepare data for MLflow evaluation
            eval_data = []
            for test_case, prediction in zip(test_data, predictions):
                eval_data.append({
                    'query': test_case['query'],
                    'expected_routing': test_case.get('should_route_to_sql', True),
                    'expected_components': test_case.get('required_components', []),
                    'prediction': prediction
                })
            
            eval_df = pd.DataFrame(eval_data)
            
            # Use custom metrics if MLflow evaluate is available
            try:
                results = mlflow.evaluate(
                    data=eval_df,
                    targets="expected_routing",
                    predictions="prediction", 
                    extra_metrics=TEXT2SQL_METRICS,
                    evaluator_config={"col_mapping": {"inputs": "query"}}
                )
                
                print("✅ MLflow native evaluation completed")
                
            except Exception as e:
                print(f"⚠️ MLflow native evaluation not available: {e}")
                
        except Exception as e:
            print(f"⚠️ Error in MLflow native evaluation: {e}")


async def main():
    """Main function to run advanced evaluation"""
    
    evaluator = AdvancedText2SQLEvaluator()
    overall_metrics, category_results = await evaluator.run_comprehensive_evaluation()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 ADVANCED EVALUATION SUMMARY")
    print("="*60)
    
    print(f"\n🎯 Key Performance Indicators:")
    print(f"  • SQL Quality: {overall_metrics.get('sql_syntax_accuracy', 0):.1%}")
    print(f"  • Routing Accuracy: {overall_metrics.get('routing_accuracy', 0):.1%}")
    print(f"  • Chart Generation: {overall_metrics.get('chart_success_rate', 0):.1%}")
    print(f"  • Multi-Intent Handling: {overall_metrics.get('multi_intent_handling', 0):.1%}")
    print(f"  • Safety Compliance: {overall_metrics.get('safety_compliance', 0):.1%}")
    
    print(f"\n📈 Category Performance:")
    for category, metrics in category_results.items():
        success_rate = metrics.get('successful_predictions', 0) / metrics.get('total_test_cases', 1)
        print(f"  • {category.replace('_', ' ').title()}: {success_rate:.1%}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())
