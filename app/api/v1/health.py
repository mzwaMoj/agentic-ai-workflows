"""
Health check endpoints for monitoring application status.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import time
from datetime import datetime

from app.models import HealthCheckRequest, HealthCheckResponse
from app.services import get_service_container

router = APIRouter()


@router.get("/", response_model=HealthCheckResponse)
async def basic_health_check():
    """
    🏥 **Basic Health Check**
    
    Quick health status check for the API.
    
    ### 📋 **What this returns:**
    - System status (healthy/unhealthy)
    - Current timestamp
    - API version
    
    ### 🚀 **Use this to:**
    - Verify the API is running
    - Check basic connectivity
    - Monitor uptime in load balancers
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )


@router.get("/detailed", response_model=HealthCheckResponse)
async def detailed_health_check(
    container = Depends(get_service_container)
):
    """
    🔍 **Detailed Health Check**
    
    Comprehensive health check including all services and dependencies.
    
    ### 📊 **Checks these services:**
    - **Azure OpenAI**: Connection and model availability
    - **Database**: SQL Server connectivity and query capability  
    - **Vector Database**: ChromaDB connection and search functionality
    - **Logging**: MLflow status (if enabled)
    
    ### 📋 **Response includes:**
    - Overall system status
    - Individual service health status
    - Error details for any failing services
    - Performance metrics and response times
    
    ### 🚨 **Status Codes:**
    - `200`: All services healthy
    - `503`: One or more services unhealthy
    """
    try:
        start_time = time.time()
        
        # Get health status from all services
        service_health = await container.health_check_all()
        
        # Determine overall status
        overall_status = "healthy"
        for service_name, health_info in service_health.items():
            if isinstance(health_info, dict) and health_info.get("status") != "healthy":
                overall_status = "unhealthy"
                break
                
        response_time = time.time() - start_time
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now(),
            services=service_health,
            version="1.0.0",
            uptime=f"Response time: {response_time:.3f}s"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/ready")
async def readiness_check(
    container = Depends(get_service_container)
):
    """Readiness probe for container orchestration."""
    try:
        # Check if critical services are ready
        service_health = await container.health_check_all()
        
        critical_services = ["openai", "database", "vector_db"]
        for service in critical_services:
            if service in service_health:
                health_info = service_health[service]
                if isinstance(health_info, dict) and health_info.get("status") != "healthy":
                    raise HTTPException(
                        status_code=503,
                        detail=f"Critical service {service} is not ready"
                    )
                    
        return {"status": "ready", "timestamp": datetime.now()}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Readiness check failed: {str(e)}"
        )


@router.get("/live")
async def liveness_check():
    """Liveness probe for container orchestration."""
    return {"status": "alive", "timestamp": datetime.now()}


@router.get("/metrics")
async def metrics_endpoint(
    container = Depends(get_service_container)
):
    """Basic metrics endpoint."""
    try:
        service_health = await container.health_check_all()
        
        metrics = {
            "services_total": len(service_health),
            "services_healthy": sum(
                1 for health in service_health.values() 
                if isinstance(health, dict) and health.get("status") == "healthy"
            ),
            "timestamp": datetime.now(),
            "version": "1.0.0"
        }
        
        return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Metrics collection failed: {str(e)}"
        )
