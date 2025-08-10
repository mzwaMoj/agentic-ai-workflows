"""
Main FastAPI application entry point.
"""



import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.api.v1 import health_router, text2sql_router, chat_router
from app.services import get_service_container
from app.utils import Text2SQLException, ResponseFormatter

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Text2SQL API application...")
    
    try:
        # Validate configuration
        settings.validate_required_settings()
        logger.info("Configuration validated successfully")
        
        # Initialize services
        container = await get_service_container()
        logger.info("Services initialized successfully")
          # Store container in app state
        app.state.service_container = container
        
        # Skip health checks during startup to avoid hanging
        # TODO: Investigate health check hanging issue
        logger.info("Skipping health checks during startup")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Text2SQL API application...")
    
    try:
        if hasattr(app.state, 'service_container'):
            await app.state.service_container.cleanup()
            logger.info("Services cleaned up successfully")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
    
    logger.info("Application shutdown completed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Text2SQL API",
        version="1.0.0",
        description="""
        ## 🚀 Text-to-SQL API
        
        A powerful API that converts natural language queries into SQL and executes them against your database.
        
        ### 🎯 Key Features
        - **Natural Language Processing**: Convert plain English questions into SQL queries
        - **Database Execution**: Execute queries against SQL Server databases  
        - **Chart Generation**: Automatically generate visualizations when appropriate
        - **Chat Interface**: Maintain conversation context for follow-up questions
        - **Health Monitoring**: Built-in health checks and monitoring
        
        ### 📊 Example Queries
        - "Which client has the highest account balance?"
        - "What are the quarterly transaction volumes?"
        - "How many closed accounts are there?"
        - "Show me customer demographics by age group"
        
        ### 🔧 Getting Started
        1. Use the `/api/v1/text2sql/generate` endpoint for natural language queries
        2. Try the examples provided in each endpoint's documentation
        3. Check `/api/v1/health` for system status
        
        ### 📚 API Documentation
        - Browse endpoints below to see detailed examples
        - Each endpoint includes multiple example requests
        - Response schemas show expected output formats
        """,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None
    )
      # Add middleware with enhanced CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware for request logging and timing
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
            
            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {str(e)} - {process_time:.3f}s")
            raise
    
    # Include API routers
    app.include_router(
        health_router,
        prefix=f"{settings.api_prefix}/health",
        tags=["Health"]
    )
    
    app.include_router(
        text2sql_router,
        prefix=f"{settings.api_prefix}/text2sql",
        tags=["Text2SQL"]
    )
    
    app.include_router(
        chat_router,
        prefix=f"{settings.api_prefix}/chat",
        tags=["Chat"]
    )
    
    # Global exception handlers
    @app.exception_handler(Text2SQLException)
    async def text2sql_exception_handler(request: Request, exc: Text2SQLException):
        """Handle Text2SQL specific exceptions."""
        logger.error(f"Text2SQL error: {exc.message}")
        
        error_response = ResponseFormatter.format_error_response(
            exc, 
            include_details=settings.debug
        )
        
        # Determine status code based on error type
        status_code = 400
        if "authentication" in exc.error_code.lower():
            status_code = 401
        elif "permission" in exc.error_code.lower():
            status_code = 403
        elif "not_found" in exc.error_code.lower():
            status_code = 404
        elif "rate_limit" in exc.error_code.lower():
            status_code = 429
        elif "service_unavailable" in exc.error_code.lower():
            status_code = 503
        elif any(keyword in exc.error_code.lower() for keyword in ["timeout", "connection", "database"]):
            status_code = 500
        
        return JSONResponse(
            status_code=status_code,
            content=error_response
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all other exceptions."""
        logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
        
        error_response = {
            "success": False,
            "error": "Internal server error",
            "timestamp": time.time()
        }
        
        if settings.debug:
            error_response["debug_info"] = {
                "error_type": type(exc).__name__,
                "error_message": str(exc)
            }
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs_url": "/docs" if settings.debug else "disabled",
            "health_check": f"{settings.api_prefix}/health"
        }
    
    return app


# Create the FastAPI application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API prefix: {settings.api_prefix}")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",  # Change from settings.host to localhost
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )