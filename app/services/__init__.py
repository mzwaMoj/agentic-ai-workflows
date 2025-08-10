"""
Services package initialization and dependency injection.
"""

import logging
from typing import Dict, Any
from app.config.settings import settings, Settings
from app.services.openai_service import OpenAIService
from app.services.database_service import DatabaseService
from app.services.vector_service import VectorService
from app.services.logging_service import LoggingService

logger = logging.getLogger(__name__)


class ServiceContainer:
    """Container for managing service dependencies."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._services: Dict[str, Any] = {}
        self._initialized = False
        
    async def initialize(self):
        """Initialize all services."""
        if self._initialized:
            return
            
        try:
            # Initialize services
            self._services['openai'] = OpenAIService(self.settings)
            self._services['database'] = DatabaseService(self.settings)
            self._services['vector'] = VectorService(self.settings)
            self._services['logging'] = LoggingService(self.settings)
            
            logger.info("All services initialized successfully")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
            
    def get_service(self, service_name: str) -> Any:
        """Get a specific service by name."""
        if not self._initialized:
            raise RuntimeError("Services not initialized. Call initialize() first.")
            
        if service_name not in self._services:
            raise ValueError(f"Service '{service_name}' not found")
            
        return self._services[service_name]
        
    def get_all_services(self) -> Dict[str, Any]:
        """Get all initialized services."""
        if not self._initialized:
            raise RuntimeError("Services not initialized. Call initialize() first.")
            
        return self._services.copy()
        
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all services."""
        if not self._initialized:
            return {"error": "Services not initialized"}
            
        health_status = {}
        
        for service_name, service in self._services.items():
            try:
                if hasattr(service, 'health_check'):
                    health_status[service_name] = await service.health_check()
                else:
                    health_status[service_name] = {
                        "service": service_name,
                        "status": "unknown",
                        "message": "No health check method available"
                    }
            except Exception as e:
                health_status[service_name] = {
                    "service": service_name,
                    "status": "unhealthy",
                    "error": str(e)
                }
                
        return health_status
        
    async def cleanup(self):
        """Cleanup all services."""
        for service_name, service in self._services.items():
            try:
                if hasattr(service, 'close'):
                    await service.close()
                elif hasattr(service, 'cleanup'):
                    await service.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up service {service_name}: {e}")


# Global service container
_service_container: ServiceContainer = None


async def get_services() -> Dict[str, Any]:
    """
    Dependency injection function for FastAPI.
    Returns all initialized services.
    """
    global _service_container
    
    if _service_container is None:
        _service_container = ServiceContainer(settings)
        await _service_container.initialize()
        
    return _service_container.get_all_services()


async def get_service_container() -> ServiceContainer:
    """Get the service container instance."""
    global _service_container
    
    if _service_container is None:
        _service_container = ServiceContainer(settings)
        await _service_container.initialize()
        
    return _service_container


# Individual service getters for dependency injection
async def get_openai_service() -> OpenAIService:
    """Get OpenAI service instance."""
    services = await get_services()
    return services['openai']


async def get_database_service() -> DatabaseService:
    """Get database service instance.""" 
    services = await get_services()
    return services['database']


async def get_vector_service() -> VectorService:
    """Get vector service instance."""
    services = await get_services()
    return services['vector']


async def get_logging_service() -> LoggingService:
    """Get logging service instance."""
    services = await get_services()
    return services['logging']


__all__ = [
    "ServiceContainer",
    "get_services",
    "get_service_container", 
    "get_openai_service",
    "get_database_service",
    "get_vector_service",
    "get_logging_service"
]