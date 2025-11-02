"""
Response Quality Evaluator - LLM as Judge

This module uses an LLM to evaluate the quality of Text2SQL responses including:
- Accuracy of natural language responses
- Helpfulness and clarity
- Correctness relative to user query
- Appropriate tone and format
"""

import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class ResponseAspect(Enum):
    """Aspects of response quality to evaluate"""
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    HELPFULNESS = "helpfulness"
    TONE = "tone"
    FORMAT = "format"


@dataclass
class QualityScore:
    """Quality score for a specific aspect"""
    aspect: ResponseAspect
    score: float  # 0-10
    reasoning: str
    suggestions: List[str]


@dataclass
class ResponseQualityResult:
    """Complete quality evaluation result"""
    overall_score: float  # 0-10
    aspect_scores: List[QualityScore]
    strengths: List[str]
    weaknesses: List[str]
    overall_feedback: str
    
    def get_aspect_score(self, aspect: ResponseAspect) -> Optional[float]:
        """Get score for specific aspect"""
        for score in self.aspect_scores:
            if score.aspect == aspect:
                return score.score
        return None


class ResponseQualityEvaluator:
    """LLM-based response quality evaluator"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        Initialize evaluator
        
        Args:
            api_key: OpenAI API key (uses env var if not provided)
            model: Model to use for evaluation
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def evaluate_response(
        self,
        user_query: str,
        system_response: str,
        expected_response: Optional[str] = None,
        sql_code: Optional[str] = None,
        sql_results: Optional[Any] = None
    ) -> ResponseQualityResult:
        """
        Evaluate response quality using LLM
        
        Args:
            user_query: Original user query
            system_response: System's response to evaluate
            expected_response: Expected/ideal response (optional)
            sql_code: Generated SQL code (optional)
            sql_results: SQL execution results (optional)
            
        Returns:
            ResponseQualityResult with scores and feedback
        """
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            user_query=user_query,
            system_response=system_response,
            expected_response=expected_response,
            sql_code=sql_code,
            sql_results=sql_results
        )
        
        # Get evaluation from LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert evaluator of Text2SQL systems. Provide detailed, objective evaluations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for consistent evaluation
                response_format={"type": "json_object"}
            )
            
            evaluation = json.loads(response.choices[0].message.content)
            
            # Parse evaluation into structured result
            return self._parse_evaluation(evaluation)
            
        except Exception as e:
            logger.error(f"Error in response evaluation: {e}")
            # Return default scores on error
            return ResponseQualityResult(
                overall_score=5.0,
                aspect_scores=[],
                strengths=[],
                weaknesses=[f"Evaluation failed: {str(e)}"],
                overall_feedback="Unable to complete evaluation"
            )
    
    def _build_evaluation_prompt(
        self,
        user_query: str,
        system_response: str,
        expected_response: Optional[str],
        sql_code: Optional[str],
        sql_results: Optional[Any]
    ) -> str:
        """Build evaluation prompt for LLM"""
        
        prompt = f"""Evaluate the quality of this Text2SQL system response.

USER QUERY:
{user_query}

SYSTEM RESPONSE:
{system_response}
"""
        
        if expected_response:
            prompt += f"""
EXPECTED RESPONSE (for reference):
{expected_response}
"""
        
        if sql_code:
            prompt += f"""
GENERATED SQL:
{sql_code}
"""
        
        if sql_results:
            prompt += f"""
SQL RESULTS:
{json.dumps(sql_results, indent=2)[:500]}...
"""
        
        prompt += """

EVALUATION CRITERIA:
Evaluate the response on these aspects (score 0-10 for each):

1. ACCURACY: Is the response factually correct based on the SQL results?
2. COMPLETENESS: Does it address all parts of the user's query?
3. CLARITY: Is the response clear, concise, and easy to understand?
4. HELPFULNESS: Does it provide value and actionable information?
5. TONE: Is the tone appropriate, professional, and friendly?
6. FORMAT: Is the response well-structured and formatted?

Provide your evaluation in this JSON format:
{
  "overall_score": <0-10>,
  "aspect_scores": [
    {
      "aspect": "accuracy",
      "score": <0-10>,
      "reasoning": "<brief explanation>",
      "suggestions": ["<improvement 1>", "<improvement 2>"]
    },
    // ... repeat for each aspect
  ],
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>"],
  "overall_feedback": "<2-3 sentence summary>"
}

Be objective, specific, and constructive in your evaluation.
"""
        
        return prompt
    
    def _parse_evaluation(self, evaluation: Dict) -> ResponseQualityResult:
        """Parse LLM evaluation into ResponseQualityResult"""
        aspect_scores = []
        
        for aspect_data in evaluation.get("aspect_scores", []):
            try:
                aspect = ResponseAspect(aspect_data["aspect"])
                aspect_scores.append(QualityScore(
                    aspect=aspect,
                    score=float(aspect_data.get("score", 5.0)),
                    reasoning=aspect_data.get("reasoning", ""),
                    suggestions=aspect_data.get("suggestions", [])
                ))
            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing aspect score: {e}")
        
        return ResponseQualityResult(
            overall_score=float(evaluation.get("overall_score", 5.0)),
            aspect_scores=aspect_scores,
            strengths=evaluation.get("strengths", []),
            weaknesses=evaluation.get("weaknesses", []),
            overall_feedback=evaluation.get("overall_feedback", "")
        )
    
    def evaluate_batch(
        self,
        test_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a batch of test results
        
        Args:
            test_results: List of test result dictionaries
            
        Returns:
            List of results with quality scores added
        """
        evaluated_results = []
        
        for result in test_results:
            # Extract relevant fields
            user_query = result.get('test_case', {}).get('query', '')
            system_response = result.get('response', '')
            sql_code = result.get('sql_code')
            sql_results = result.get('sql_results')
            
            # Skip if no response to evaluate
            if not system_response:
                evaluated_results.append(result)
                continue
            
            # Evaluate response
            quality_result = self.evaluate_response(
                user_query=user_query,
                system_response=system_response,
                sql_code=sql_code,
                sql_results=sql_results
            )
            
            # Add quality scores to result
            result['quality_evaluation'] = {
                'overall_score': quality_result.overall_score,
                'aspect_scores': {
                    score.aspect.value: {
                        'score': score.score,
                        'reasoning': score.reasoning
                    }
                    for score in quality_result.aspect_scores
                },
                'strengths': quality_result.strengths,
                'weaknesses': quality_result.weaknesses,
                'feedback': quality_result.overall_feedback
            }
            
            evaluated_results.append(result)
        
        return evaluated_results
    
    def calculate_average_quality_score(self, evaluated_results: List[Dict]) -> Dict[str, float]:
        """Calculate average quality scores across all results"""
        scores = {
            'overall': [],
            'accuracy': [],
            'completeness': [],
            'clarity': [],
            'helpfulness': [],
            'tone': [],
            'format': []
        }
        
        for result in evaluated_results:
            quality_eval = result.get('quality_evaluation', {})
            
            if quality_eval:
                scores['overall'].append(quality_eval.get('overall_score', 0))
                
                for aspect, data in quality_eval.get('aspect_scores', {}).items():
                    if aspect in scores:
                        scores[aspect].append(data.get('score', 0))
        
        # Calculate averages
        averages = {}
        for aspect, score_list in scores.items():
            if score_list:
                averages[f'avg_{aspect}_score'] = sum(score_list) / len(score_list)
            else:
                averages[f'avg_{aspect}_score'] = 0.0
        
        return averages


# Convenience function for quick evaluation
def quick_evaluate(user_query: str, system_response: str) -> float:
    """
    Quick evaluation - returns overall score (0-10)
    
    Args:
        user_query: User's query
        system_response: System's response
        
    Returns:
        Overall quality score (0-10)
    """
    try:
        evaluator = ResponseQualityEvaluator()
        result = evaluator.evaluate_response(user_query, system_response)
        return result.overall_score
    except Exception as e:
        logger.error(f"Quick evaluation failed: {e}")
        return 5.0  # Default middle score


if __name__ == "__main__":
    # Example usage
    print("🧪 Response Quality Evaluator - Test")
    print("=" * 60)
    
    # Test case
    user_query = "Show me the top 10 customers by balance"
    system_response = """Based on your request, here are the top 10 customers by balance:

1. John Smith - $125,450.00
2. Jane Doe - $118,230.50
3. Robert Johnson - $95,678.25
...

These customers have the highest account balances in our system."""
    
    sql_code = """
    SELECT TOP 10 
        full_name, 
        balance 
    FROM customer_information 
    ORDER BY balance DESC
    """
    
    try:
        evaluator = ResponseQualityEvaluator()
        result = evaluator.evaluate_response(
            user_query=user_query,
            system_response=system_response,
            sql_code=sql_code
        )
        
        print(f"\n📊 Overall Score: {result.overall_score}/10")
        print(f"\n✅ Strengths:")
        for strength in result.strengths:
            print(f"   • {strength}")
        
        print(f"\n⚠️  Weaknesses:")
        for weakness in result.weaknesses:
            print(f"   • {weakness}")
        
        print(f"\n💬 Feedback: {result.overall_feedback}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nℹ️  Make sure OPENAI_API_KEY is set in your environment")
