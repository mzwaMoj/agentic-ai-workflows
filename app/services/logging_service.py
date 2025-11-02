"""
Logging service for MLflow integration and application logging.
"""

import json
import logging
from typing import Dict, Any, Optional
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class LoggingService:
    """Service for managing MLflow logging and application logging."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.mlflow_enabled = settings.enable_mlflow
        self.mlflow = None
        
        if self.mlflow_enabled:
            try:
                import mlflow
                self.mlflow = mlflow
                self._initialize_mlflow()
            except ImportError:
                logger.warning("MLflow not installed, logging disabled")
                self.mlflow_enabled = False
        else:
            logger.info("MLflow logging disabled by configuration")
        self._setup_logging()
        
    def _initialize_mlflow(self):
        """Initialize MLflow configuration."""
        if not self.mlflow:
            return
            
        try:
            # Enable MLflow OpenAI autolog
            self.mlflow.openai.autolog()
            
            # Set tracking URI if provided
            if self.settings.mlflow_tracking_uri:
                self.mlflow.set_tracking_uri(self.settings.mlflow_tracking_uri)
            # Handle experiment creation/restoration
            experiment_name = self.settings.mlflow_experiment_name
            try:
                # First try to get the experiment
                experiment = self.mlflow.get_experiment_by_name(experiment_name)
                
                if experiment is None:
                    # Experiment doesn't exist, create it
                    logger.info(f"Creating new MLflow experiment: {experiment_name}")
                    self.mlflow.create_experiment(experiment_name)
                elif experiment.lifecycle_stage == "deleted":
                    # Experiment is deleted, restore it using MLflow client
                    logger.info(f"Restoring deleted MLflow experiment: {experiment_name}")
                    client = self.mlflow.client.MlflowClient()
                    client.restore_experiment(experiment.experiment_id)
                
                # Now set the experiment
                self.mlflow.set_experiment(experiment_name)
                
            except Exception as exp_error:
                logger.warning(f"Failed to handle experiment '{experiment_name}': {exp_error}")
                # Just try to set the experiment anyway - it might exist and be usable
                try:
                    self.mlflow.set_experiment(experiment_name)
                    logger.info(f"Successfully set existing experiment: {experiment_name}")
                except Exception as set_error:
                    # Try to create the experiment if it really doesn't exist
                    logger.warning(f"Failed to set experiment '{experiment_name}': {set_error}")
                    try:
                        logger.info(f"Attempting to create experiment: {experiment_name}")
                        self.mlflow.create_experiment(experiment_name)
                        self.mlflow.set_experiment(experiment_name)
                        logger.info(f"Successfully created and set experiment: {experiment_name}")
                    except Exception as create_error:
                        logger.error(f"Failed to create experiment '{experiment_name}': {create_error}")
                        logger.warning("MLflow experiment setup failed - continuing without MLflow logging")
                        self.mlflow_enabled = False
                        return
                        return
            
            logger.info("MLflow logging initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize MLflow: {e}")
            self.mlflow_enabled = False
            # Don't raise - logging should be optional

    def _setup_logging(self):
        """Setup application logging configuration."""
        import os
        from pathlib import Path
        from datetime import datetime
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("./app/logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session-based log filename (one per day or session)
        # Check if we already have a log file for today
        today = datetime.now().strftime("%Y%m%d")
        log_file = logs_dir / f"session_{today}.log"
        
        # If no handlers exist or they don't include our file handler, set up logging
        root_logger = logging.getLogger()
        existing_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler) and str(log_file) in str(h.baseFilename)]
        
        if not existing_handlers:
            # Configure logging to both file and console (only if not already configured)
            logging.basicConfig(
                level=getattr(logging, self.settings.log_level.upper()),
                format=self.settings.log_format,
                handlers=[
                    logging.FileHandler(log_file, mode='a'),  # Append mode for session continuity
                    logging.StreamHandler()
                ],
                force=True  # Override any existing configuration
            )

    
    def start_chat_run(self, user_input: str):
        """Start a new chat run for MLflow tracking."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import start_chat_run
            start_chat_run(user_input)
        except Exception as e:
            logger.error(f"Failed to start chat run: {e}")
    
    def end_chat_run(self):
        """End the current chat run for MLflow tracking.""" 
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import end_chat_run
            end_chat_run()
        except Exception as e:
            logger.error(f"Failed to end chat run: {e}")
            
    def log_router_response(self, message):
        """Log router response to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            # Convert message to JSON-safe format before logging
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Convert tool_calls to serializable format
                serializable_message = {
                    "content": getattr(message, 'content', ''),  # Get content or empty string
                    "role": getattr(message, 'role', 'assistant'),
                    "tool_calls": []
                }
                for tool_call in message.tool_calls:
                    serializable_message["tool_calls"].append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
                from app.utils import log_router_response
                log_router_response(json.dumps(serializable_message, indent=2))  # Convert to JSON string
            else:
                from app.utils import log_router_response
                log_router_response(str(message))
        except Exception as e:
            logger.error(f"Failed to log router response: {e}")
    
    def log_table_retriever_response(self, response):
        """Log table retriever response to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_table_retriever_response
            log_table_retriever_response(response)
        except Exception as e:
            logger.error(f"Failed to log table retriever response: {e}")
    
    def log_sql_code(self, sql_code: str):
        """Log generated SQL code to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_sql_code
            log_sql_code(sql_code)
        except Exception as e:
            logger.error(f"Failed to log SQL code: {e}")
    
    def log_sql_results(self, results):
        """Log SQL execution results to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_sql_results
            log_sql_results(results)
        except Exception as e:
            logger.error(f"Failed to log SQL results: {e}")
    
    def log_generated_chart_results(self, results):
        """Log chart generation results to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_generated_chart_results
            log_generated_chart_results(results)
        except Exception as e:
            logger.error(f"Failed to log chart results: {e}")

    def log_products(self, results):
        """Log chart generation results to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_products
            log_products(results)
        except Exception as e:
            logger.error(f"Failed to log chart results: {e}")
    
    def log_polish_prompt(self, prompt):
        """Log polish prompt to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_polish_prompt
            log_polish_prompt(prompt)
        except Exception as e:
            logger.error(f"Failed to log polish prompt: {e}")
            
    def log_sql_analysis_error(self, error: str):
        """Log SQL analysis error to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_sql_analysis_error
            log_sql_analysis_error(error)
        except Exception as e:
            logger.error(f"Failed to log SQL analysis error: {e}")
            
    def log_final_response(self, response: str):
        """Log final response to MLflow."""
        if not self.mlflow_enabled:
            return
        try:
            from app.utils import log_final_response
            log_final_response(response)
        except Exception as e:
            logger.error(f"Failed to log final response: {e}")
            
    def log_error(self, error_message: str):
        """Log general error message."""
        logger.error(error_message)
        
        # Also log to MLflow if possible
        if self.mlflow_enabled and self.mlflow:
            try:
                self.mlflow.log_param("error", error_message)
            except Exception:
                pass  # Don't fail if MLflow logging fails
            
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for logging service."""
        try:
            if self.mlflow_enabled and self.mlflow:
                # Check if MLflow is accessible
                experiment = self.mlflow.get_experiment_by_name(self.settings.mlflow_experiment_name)
                
                return {
                    "service": "logging",
                    "status": "healthy",
                    "mlflow_experiment": self.settings.mlflow_experiment_name,
                    "experiment_id": experiment.experiment_id if experiment else None,
                    "log_level": self.settings.log_level
                }
            else:                
                return {
                    "service": "logging", 
                    "status": "healthy",
                    "mlflow_enabled": False,
                    "log_level": self.settings.log_level
                }
            
        except Exception as e:
            return {
                "service": "logging",
                "status": "unhealthy",
                "error": str(e),
                "mlflow_experiment": self.settings.mlflow_experiment_name,
                "log_level": self.settings.log_level
            }
