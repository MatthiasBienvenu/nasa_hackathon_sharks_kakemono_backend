from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "message": "Welcome to NASA Hackathon Sharks Kakemono Backend API"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "nasa_hackathon_sharks_kakemono_backend"
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "NASA Hackathon Sharks Kakemono Backend",
        "version": "0.1.0",
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Root endpoint"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/api/v1/info", "method": "GET", "description": "API information"},
            {"path": "/docs", "method": "GET", "description": "Interactive API documentation"},
            {"path": "/redoc", "method": "GET", "description": "ReDoc API documentation"}
        ]
    }


@app.get("/api/v1/sharks")
async def api_sharks():
    pass
