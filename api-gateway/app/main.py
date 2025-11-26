from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
import os
from typing import Optional

app = FastAPI(title="IT Management API Gateway", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs de los microservicios
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "equipment": os.getenv("EQUIPMENT_SERVICE_URL", "http://equipment-service:8002"),
    "provider": os.getenv("PROVIDER_SERVICE_URL", "http://provider-service:8003"),
    "maintenance": os.getenv("MAINTENANCE_SERVICE_URL", "http://maintenance-service:8004"),
    "reports": os.getenv("REPORTS_SERVICE_URL", "http://reports-service:8005"),
}

# Cliente HTTP
async_client = httpx.AsyncClient(timeout=30.0)

@app.on_event("shutdown")
async def shutdown_event():
    await async_client.aclose()

@app.get("/")
def read_root():
    return {
        "service": "IT Management API Gateway",
        "version": "1.0.0",
        "status": "running",
        "services": list(SERVICES.keys())
    }

@app.get("/health")
async def health_check():
    """Verificar salud de todos los servicios"""
    health_status = {"gateway": "healthy", "services": {}}

    for service_name, service_url in SERVICES.items():
        try:
            response = await async_client.get(f"{service_url}/health", timeout=5.0)
            health_status["services"][service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": service_url
            }
        except Exception as e:
            health_status["services"][service_name] = {
                "status": "unreachable",
                "url": service_url,
                "error": str(e)
            }

    return health_status

async def forward_request(
    service: str,
    path: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Reenviar petición al microservicio correspondiente"""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")

    service_url = SERVICES[service]
    target_url = f"{service_url}/{path}"

    # Preparar headers
    headers = dict(request.headers)
    if authorization:
        headers["Authorization"] = authorization

    # Leer el body
    body = await request.body()

    try:
        # Reenviar la petición
        response = await async_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=request.query_params
        )

        # Si es una respuesta de archivo (PDF, Excel), devolver StreamingResponse
        content_type = response.headers.get("content-type", "")
        if "application/pdf" in content_type or "spreadsheet" in content_type:
            return StreamingResponse(
                iter([response.content]),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type
            )

        # Respuesta JSON normal
        return JSONResponse(
            content=response.json() if response.content else {},
            status_code=response.status_code
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service {service} unavailable: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gateway error: {str(e)}"
        )

# ============================================
# AUTH SERVICE ROUTES
# ============================================

@app.api_route("/api/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def auth_proxy(path: str, request: Request, authorization: Optional[str] = Header(None)):
    return await forward_request("auth", path, request, authorization)

# ============================================
# EQUIPMENT SERVICE ROUTES
# ============================================

@app.api_route("/api/equipment/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def equipment_proxy(path: str, request: Request, authorization: Optional[str] = Header(None)):
    return await forward_request("equipment", path, request, authorization)

# ============================================
# PROVIDER SERVICE ROUTES
# ============================================

@app.api_route("/api/providers/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def provider_proxy(path: str, request: Request, authorization: Optional[str] = Header(None)):
    return await forward_request("provider", path, request, authorization)

# ============================================
# MAINTENANCE SERVICE ROUTES
# ============================================

@app.api_route("/api/maintenance/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def maintenance_proxy(path: str, request: Request, authorization: Optional[str] = Header(None)):
    return await forward_request("maintenance", path, request, authorization)

# ============================================
# REPORTS SERVICE ROUTES
# ============================================

@app.api_route("/api/reports/{path:path}", methods=["GET", "POST"])
async def reports_proxy(path: str, request: Request, authorization: Optional[str] = Header(None)):
    return await forward_request("reports", path, request, authorization)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
