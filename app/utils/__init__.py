"""
Utils package initialization.
"""

from .exceptions import (
    Text2SQLException,
    SQLGenerationError,
    SQLExecutionError,
    SQLValidationError,
    DatabaseConnectionError,
    VectorDatabaseError,
    ChartGenerationError,
    TableNotFoundError,
    InvalidQueryError,
    AuthenticationError,
    ConfigurationError,
    ServiceUnavailableError,
    RateLimitError,
    TimeoutError,
    DataValidationError,
    PermissionError
)

from .validators import (
    QueryValidator,
    DataValidator,
    validate_request_data,
    validate_pagination_params
)

from .formatters import (
    ResponseFormatter,
    DataFormatter
)

from .generate_charts import execute_plot_code

from .mlflow_logger import (
    start_chat_run,
    log_router_response,
    log_table_retriever_response,
    log_sql_code,
    log_sql_results,
    log_generated_chart_results,
    log_sql_analysis_error,
    log_required_tables,
    log_polish_prompt,
    log_final_response,
    log_products,
    end_chat_run
)

__all__ = [
    # Exceptions
    "Text2SQLException",
    "SQLGenerationError", 
    "SQLExecutionError",
    "SQLValidationError",
    "DatabaseConnectionError",
    "VectorDatabaseError",
    "ChartGenerationError",
    "TableNotFoundError",
    "InvalidQueryError",
    "AuthenticationError",
    "ConfigurationError",
    "ServiceUnavailableError",
    "RateLimitError",
    "TimeoutError",
    "DataValidationError",
    "PermissionError",
    
    # Validators
    "QueryValidator",
    "DataValidator",
    "validate_request_data",
    "validate_pagination_params",
    
    # Formatters
    "ResponseFormatter",
    "DataFormatter",

    # Chart Generation
    "execute_plot_code",
    
    # MLflow Logging Functions
    "start_chat_run",
    "log_router_response", 
    "log_table_retriever_response",
    "log_sql_code",
    "log_sql_results",
    "log_generated_chart_results",
    "log_sql_analysis_error",
    "log_required_tables", 
    "log_polish_prompt",
    "log_final_response",
    "log_products",
    "end_chat_run"
]