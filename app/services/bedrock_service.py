# Bedrock Integration Service for Text2SQL AI Analyst
# This module provides a comprehensive interface to Amazon Bedrock for LLM operations

import json
import boto3
import asyncio
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from botocore.exceptions import ClientError, BotoCoreError
import logging
from functools import wraps
import time
import hashlib
from dataclasses import dataclass
from enum import Enum
import tiktoken

# Configure logging
logger = logging.getLogger(__name__)

class BedrockModelType(Enum):
    """Enumeration of supported Bedrock models"""
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
    TITAN_TEXT_LARGE = "amazon.titan-text-lite-v1"
    TITAN_EMBED = "amazon.titan-embed-text-v1"
    LLAMA_2_70B = "meta.llama2-70b-chat-v1"
    LLAMA_2_13B = "meta.llama2-13b-chat-v1"

@dataclass
class BedrockRequest:
    """Data class for Bedrock API requests"""
    model_id: str
    prompt: str
    max_tokens: int = 4096
    temperature: float = 0.1
    top_p: float = 0.9
    top_k: int = 250
    stop_sequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class BedrockResponse:
    """Data class for Bedrock API responses"""
    model_id: str
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    timestamp: datetime
    request_id: str
    metadata: Optional[Dict[str, Any]] = None

class BedrockCircuitBreaker:
    """Circuit breaker pattern for Bedrock API calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func):
        """Decorator to implement circuit breaker pattern"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise Exception("Circuit breaker is OPEN - service unavailable")
            
            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    logger.info("Circuit breaker reset to CLOSED")
                return result
                
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(f"Circuit breaker opened due to {self.failure_count} failures")
                
                raise e
        
        return wrapper

class BedrockRateLimiter:
    """Rate limiter for Bedrock API calls"""
    
    def __init__(self, max_requests_per_minute: int = 100):
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire rate limit permission"""
        async with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests if now - req_time < 60]
            
            if len(self.requests) >= self.max_requests:
                sleep_time = 60 - (now - self.requests[0])
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                return await self.acquire()
            
            self.requests.append(now)

class BedrockPromptManager:
    """Manages prompt templates and versioning"""
    
    def __init__(self, s3_client, bucket_name: str):
        self.s3_client = s3_client
        self.bucket_name = bucket_name
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    async def get_prompt_template(self, template_name: str, version: str = "latest") -> str:
        """Retrieve prompt template from S3 with caching"""
        cache_key = f"{template_name}:{version}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['content']
        
        try:
            # Fetch from S3
            key = f"prompts/{template_name}/{version}.txt"
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            # Cache the result
            self.cache[cache_key] = {
                'content': content,
                'timestamp': time.time()
            }
            
            return content
            
        except ClientError as e:
            logger.error(f"Failed to fetch prompt template {template_name}:{version}: {e}")
            raise
    
    async def save_prompt_template(self, template_name: str, content: str, metadata: Dict = None) -> str:
        """Save new prompt template version to S3"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        version = f"v{timestamp}"
        
        try:
            # Save versioned template
            key = f"prompts/{template_name}/{version}.txt"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content.encode('utf-8'),
                Metadata=metadata or {}
            )
            
            # Update latest pointer
            latest_key = f"prompts/{template_name}/latest.txt"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=latest_key,
                Body=content.encode('utf-8')
            )
            
            # Clear cache
            cache_keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{template_name}:")]
            for key in cache_keys_to_remove:
                del self.cache[key]
            
            logger.info(f"Saved prompt template {template_name} as version {version}")
            return version
            
        except ClientError as e:
            logger.error(f"Failed to save prompt template {template_name}: {e}")
            raise

class BedrockMetricsCollector:
    """Collects and publishes metrics to CloudWatch"""
    
    def __init__(self, cloudwatch_client):
        self.cloudwatch_client = cloudwatch_client
        self.namespace = "Text2SQL/Bedrock"
    
    async def publish_metrics(self, response: BedrockResponse, error: Optional[Exception] = None):
        """Publish metrics to CloudWatch"""
        try:
            metrics = [
                {
                    'MetricName': 'InvocationLatency',
                    'Value': response.latency_ms,
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'ModelId', 'Value': response.model_id}
                    ]
                },
                {
                    'MetricName': 'InputTokens',
                    'Value': response.input_tokens,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'ModelId', 'Value': response.model_id}
                    ]
                },
                {
                    'MetricName': 'OutputTokens',
                    'Value': response.output_tokens,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'ModelId', 'Value': response.model_id}
                    ]
                }
            ]
            
            if error:
                metrics.append({
                    'MetricName': 'InvocationErrors',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'ModelId', 'Value': response.model_id if response else 'unknown'},
                        {'Name': 'ErrorType', 'Value': type(error).__name__}
                    ]
                })
            else:
                metrics.append({
                    'MetricName': 'SuccessfulInvocations',
                    'Value': 1,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'ModelId', 'Value': response.model_id}
                    ]
                })
            
            self.cloudwatch_client.put_metric_data(
                Namespace=self.namespace,
                MetricData=metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to publish metrics: {e}")

class BedrockService:
    """Main service class for Amazon Bedrock integration"""
    
    def __init__(self, 
                 region_name: str = "us-east-1",
                 s3_bucket_name: Optional[str] = None,
                 rate_limit_per_minute: int = 100):
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        self.s3_client = boto3.client('s3', region_name=region_name) if s3_bucket_name else None
        self.cloudwatch_client = boto3.client('cloudwatch', region_name=region_name)
        
        # Initialize components
        self.circuit_breaker = BedrockCircuitBreaker()
        self.rate_limiter = BedrockRateLimiter(rate_limit_per_minute)
        self.prompt_manager = BedrockPromptManager(self.s3_client, s3_bucket_name) if s3_bucket_name else None
        self.metrics_collector = BedrockMetricsCollector(self.cloudwatch_client)
        
        # Model configurations
        self.model_configs = {
            BedrockModelType.CLAUDE_3_SONNET.value: {
                "max_tokens": 4096,
                "temperature": 0.1,
                "top_p": 0.9,
                "anthropic_version": "bedrock-2023-05-31"
            },
            BedrockModelType.CLAUDE_3_HAIKU.value: {
                "max_tokens": 4096,
                "temperature": 0.3,
                "top_p": 0.9,
                "anthropic_version": "bedrock-2023-05-31"
            },
            BedrockModelType.TITAN_TEXT_LARGE.value: {
                "maxTokenCount": 4096,
                "temperature": 0.1,
                "topP": 0.9
            },
            BedrockModelType.LLAMA_2_70B.value: {
                "max_gen_len": 2048,
                "temperature": 0.1,
                "top_p": 0.9
            }
        }
    
    def _prepare_claude_payload(self, request: BedrockRequest) -> Dict:
        """Prepare payload for Claude models"""
        return {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "messages": [
                {
                    "role": "user",
                    "content": request.prompt
                }
            ],
            "stop_sequences": request.stop_sequences or []
        }
    
    def _prepare_titan_payload(self, request: BedrockRequest) -> Dict:
        """Prepare payload for Titan models"""
        return {
            "inputText": request.prompt,
            "textGenerationConfig": {
                "maxTokenCount": request.max_tokens,
                "temperature": request.temperature,
                "topP": request.top_p,
                "stopSequences": request.stop_sequences or []
            }
        }
    
    def _prepare_llama_payload(self, request: BedrockRequest) -> Dict:
        """Prepare payload for Llama models"""
        return {
            "prompt": request.prompt,
            "max_gen_len": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p
        }
    
    def _prepare_payload(self, request: BedrockRequest) -> Dict:
        """Prepare payload based on model type"""
        if "claude" in request.model_id:
            return self._prepare_claude_payload(request)
        elif "titan" in request.model_id:
            return self._prepare_titan_payload(request)
        elif "llama" in request.model_id:
            return self._prepare_llama_payload(request)
        else:
            raise ValueError(f"Unsupported model: {request.model_id}")
    
    def _parse_claude_response(self, response_body: Dict, request_id: str) -> Dict:
        """Parse Claude model response"""
        content = response_body.get('content', [{}])[0].get('text', '')
        usage = response_body.get('usage', {})
        
        return {
            'content': content,
            'input_tokens': usage.get('input_tokens', 0),
            'output_tokens': usage.get('output_tokens', 0)
        }
    
    def _parse_titan_response(self, response_body: Dict, request_id: str) -> Dict:
        """Parse Titan model response"""
        results = response_body.get('results', [{}])
        content = results[0].get('outputText', '') if results else ''
        
        # Estimate tokens (Titan doesn't return token counts)
        input_tokens = len(response_body.get('inputTextTokenCount', 0))
        output_tokens = len(content.split()) * 1.3  # Rough estimation
        
        return {
            'content': content,
            'input_tokens': int(input_tokens),
            'output_tokens': int(output_tokens)
        }
    
    def _parse_llama_response(self, response_body: Dict, request_id: str) -> Dict:
        """Parse Llama model response"""
        content = response_body.get('generation', '')
        
        # Estimate tokens (Llama doesn't return token counts)
        input_tokens = len(response_body.get('prompt', '').split()) * 1.3
        output_tokens = len(content.split()) * 1.3
        
        return {
            'content': content,
            'input_tokens': int(input_tokens),
            'output_tokens': int(output_tokens)
        }
    
    def _parse_response(self, response_body: Dict, model_id: str, request_id: str) -> Dict:
        """Parse response based on model type"""
        if "claude" in model_id:
            return self._parse_claude_response(response_body, request_id)
        elif "titan" in model_id:
            return self._parse_titan_response(response_body, request_id)
        elif "llama" in model_id:
            return self._parse_llama_response(response_body, request_id)
        else:
            raise ValueError(f"Unsupported model: {model_id}")
    
    @BedrockCircuitBreaker.call
    async def invoke_model(self, request: BedrockRequest) -> BedrockResponse:
        """Invoke Bedrock model with comprehensive error handling and monitoring"""
        
        # Apply rate limiting
        await self.rate_limiter.acquire()
        
        start_time = time.time()
        request_id = hashlib.md5(f"{request.model_id}{request.prompt}{start_time}".encode()).hexdigest()[:8]
        
        try:
            logger.info(f"Invoking Bedrock model {request.model_id} (request_id: {request_id})")
            
            # Prepare payload
            payload = self._prepare_payload(request)
            
            # Make API call
            response = self.bedrock_client.invoke_model(
                modelId=request.model_id,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            parsed_response = self._parse_response(response_body, request.model_id, request_id)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Create response object
            bedrock_response = BedrockResponse(
                model_id=request.model_id,
                content=parsed_response['content'],
                input_tokens=parsed_response['input_tokens'],
                output_tokens=parsed_response['output_tokens'],
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                request_id=request_id,
                metadata=request.metadata
            )
            
            # Publish metrics
            await self.metrics_collector.publish_metrics(bedrock_response)
            
            logger.info(f"Successfully invoked model {request.model_id} "
                       f"(latency: {latency_ms}ms, tokens: {parsed_response['output_tokens']})")
            
            return bedrock_response
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            logger.error(f"Bedrock API error for model {request.model_id}: {error_code} - {error_message}")
            
            # Publish error metrics
            if 'bedrock_response' in locals():
                await self.metrics_collector.publish_metrics(bedrock_response, e)
            
            raise Exception(f"Bedrock API error: {error_code} - {error_message}")
            
        except Exception as e:
            logger.error(f"Unexpected error invoking model {request.model_id}: {str(e)}")
            
            # Publish error metrics
            if 'bedrock_response' in locals():
                await self.metrics_collector.publish_metrics(bedrock_response, e)
            
            raise
    
    async def generate_text2sql(self, 
                               natural_language_query: str,
                               table_metadata: Dict,
                               model_id: str = BedrockModelType.CLAUDE_3_SONNET.value,
                               temperature: float = 0.1) -> BedrockResponse:
        """Generate SQL from natural language query"""
        
        # Get prompt template
        if self.prompt_manager:
            prompt_template = await self.prompt_manager.get_prompt_template("text2sql")
        else:
            # Fallback prompt template
            prompt_template = """
You are an expert SQL analyst. Convert the following natural language query to SQL.

Table Schema:
{table_metadata}

Natural Language Query: {natural_language_query}

Requirements:
1. Generate only valid SQL
2. Use proper table and column names
3. Include appropriate WHERE clauses
4. Optimize for performance
5. Return only the SQL query, no explanations

SQL Query:
"""
        
        # Format prompt
        formatted_prompt = prompt_template.format(
            table_metadata=json.dumps(table_metadata, indent=2),
            natural_language_query=natural_language_query
        )
        
        # Create request
        request = BedrockRequest(
            model_id=model_id,
            prompt=formatted_prompt,
            max_tokens=2048,
            temperature=temperature,
            metadata={
                'use_case': 'text2sql',
                'natural_language_query': natural_language_query
            }
        )
        
        return await self.invoke_model(request)
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Titan Embeddings model"""
        
        embeddings = []
        
        for text in texts:
            request = BedrockRequest(
                model_id=BedrockModelType.TITAN_EMBED.value,
                prompt=text,
                metadata={'use_case': 'embeddings'}
            )
            
            try:
                # Prepare payload for embeddings
                payload = {"inputText": text}
                
                response = self.bedrock_client.invoke_model(
                    modelId=BedrockModelType.TITAN_EMBED.value,
                    body=json.dumps(payload),
                    contentType="application/json",
                    accept="application/json"
                )
                
                response_body = json.loads(response['body'].read())
                embedding = response_body.get('embedding', [])
                embeddings.append(embedding)
                
            except Exception as e:
                logger.error(f"Failed to generate embedding for text: {e}")
                embeddings.append([])
        
        return embeddings
    
    async def optimize_sql_query(self, sql_query: str, explain_plan: str = None) -> BedrockResponse:
        """Optimize SQL query using LLM"""
        
        # Get optimization prompt template
        if self.prompt_manager:
            prompt_template = await self.prompt_manager.get_prompt_template("sql_optimization")
        else:
            prompt_template = """
You are a SQL optimization expert. Analyze and optimize the following SQL query for better performance.

Original SQL Query:
{sql_query}

Execution Plan (if available):
{explain_plan}

Provide:
1. Optimized SQL query
2. Explanation of optimizations made
3. Performance improvement recommendations

Optimized Query:
"""
        
        formatted_prompt = prompt_template.format(
            sql_query=sql_query,
            explain_plan=explain_plan or "Not provided"
        )
        
        request = BedrockRequest(
            model_id=BedrockModelType.LLAMA_2_70B.value,
            prompt=formatted_prompt,
            max_tokens=2048,
            temperature=0.0,
            metadata={
                'use_case': 'sql_optimization',
                'original_query': sql_query
            }
        )
        
        return await self.invoke_model(request)
    
    async def analyze_query_results(self, 
                                  query_results: List[Dict],
                                  natural_language_query: str) -> BedrockResponse:
        """Analyze query results and provide insights"""
        
        # Limit results for analysis (to avoid token limits)
        sample_results = query_results[:100]
        
        if self.prompt_manager:
            prompt_template = await self.prompt_manager.get_prompt_template("result_analysis")
        else:
            prompt_template = """
You are a data analyst. Analyze the following query results and provide insights.

Original Question: {natural_language_query}

Query Results (sample):
{query_results}

Provide:
1. Key insights from the data
2. Notable patterns or trends
3. Summary statistics
4. Recommendations for further analysis

Analysis:
"""
        
        formatted_prompt = prompt_template.format(
            natural_language_query=natural_language_query,
            query_results=json.dumps(sample_results, indent=2, default=str)
        )
        
        request = BedrockRequest(
            model_id=BedrockModelType.CLAUDE_3_HAIKU.value,
            prompt=formatted_prompt,
            max_tokens=1024,
            temperature=0.3,
            metadata={
                'use_case': 'result_analysis',
                'result_count': len(query_results)
            }
        )
        
        return await self.invoke_model(request)

# Usage Examples and Testing
async def main():
    """Example usage of BedrockService"""
    
    # Initialize service
    bedrock_service = BedrockService(
        region_name="us-east-1",
        s3_bucket_name="your-prompt-bucket",
        rate_limit_per_minute=100
    )
    
    # Example 1: Text2SQL Generation
    table_metadata = {
        "customers": {
            "columns": ["id", "name", "email", "created_date"],
            "types": ["int", "varchar", "varchar", "datetime"]
        },
        "orders": {
            "columns": ["id", "customer_id", "amount", "order_date"],
            "types": ["int", "int", "decimal", "datetime"]
        }
    }
    
    try:
        response = await bedrock_service.generate_text2sql(
            natural_language_query="Show me the top 10 customers by total order value",
            table_metadata=table_metadata
        )
        
        print(f"Generated SQL: {response.content}")
        print(f"Latency: {response.latency_ms}ms")
        print(f"Tokens used: {response.input_tokens + response.output_tokens}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
