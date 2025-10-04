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

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
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

## Project Structure

```
nasa_hackathon_sharks_kakemono_backend/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── LICENSE             # MIT License
└── .gitignore          # Git ignore rules
```

## License

MIT License - see LICENSE file for details