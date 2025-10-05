import io
from matplotlib import pyplot as plt
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from shark.eddy import data_cyclones, data_anticyclones
from shark.simu import *

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def start_shark_simulation():
    # Launch simulation in the background
    asyncio.create_task(simulate_sharks(sharks))


@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "message": "Kakemono sharks backend API"
    }


@app.get("/api/v1/info")
async def api_info():
    """API information endpoint"""
    return {
        "version": "0.1.0",
        "endpoints": [
            {
                "path": "/",
                "method": "GET",
                "description": "Root endpoint - welcome message"
            },
            {
                "path": "/api/v1/info",
                "method": "GET",
                "description": "API information endpoint"
            },
            {
                "path": "/api/v1/get_eddies_data",
                "method": "GET",
                "description": "Returns cyclones and anticyclones data"
            },
            {
                "path": "/api/v1/get_shark_positions",
                "method": "GET",
                "description": "Returns current positions of all sharks"
            }
        ]
    }


@app.get("/api/v1/get_eddies_data")
async def api_get_cyclones():
    """Get list of cyclones"""
    return {
        "cyclones": data_cyclones,
        "anticyclones": data_anticyclones
    }


@app.get("/api/v1/get_shark_positions")
async def api_get_shark_positions():
    """Get list of sharks"""
    return {
        "positions": get_shark_positions(sharks)
    }


@app.get("/api/v1/get_eddies_heatmap")
async def api_get_eddies_heatmap():
    """Get a heatmap of the eddies"""
    return FileResponse(
        "shark/eddies_heatmap.png",
        media_type="image/png",
        filename="eddies_heatmap.png"
    )


@app.get("api/v1/get_local_temperature_graph")
async def api_get_local_temperature_graph():
    return FileResponse(
        "shark/temperature.jpg",
        media_type="image/jpg",
        filename="temperatureAnticyclone.jpg"
    )








