# NASA Hackathon Sharks Kakemono Backend

A FastAPI-based backend API for the NASA Hackathon Sharks Kakemono project.

## Features

- FastAPI framework for high performance
- Interactive API documentation (Swagger UI)
- CORS middleware enabled
- Health check endpoint
- RESTful API structure

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MatthiasBienvenu/nasa_hackathon_sharks_kakemono_backend.git
cd nasa_hackathon_sharks_kakemono_backend
```

2. Download _uv_ for python environment management
``` bash
# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# if you don't have curl
wget -qO- https://astral.sh/uv/install.sh | sh
```
```bash
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Create a virtual environment:
```bash
uv venv
```

4. Activate or deactivate the venv
``` bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
deactivate
```

5. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`

## Available Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check endpoint
- `GET /api/v1/info` - API information

## License

MIT License - see LICENSE file for details
