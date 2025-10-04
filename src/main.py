from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NASA Hackathon Sharks Kakemono Backend",
    description="Backend API for NASA Hackathon Sharks Kakemono project",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "message": "Welcome to NASA Hackathon Sharks Kakemono Backend API",
        "version": "0.1.0"
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
