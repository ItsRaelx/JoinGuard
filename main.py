import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from routes.api import api_router
from routes.list import list_router
from routes.login import login_router
from routes.report import report_router

# Load environment variables
env_path = '.env'
if os.path.exists(env_path):
    load_dotenv(env_path)

# Get environment variables
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')

app = FastAPI(
    title="JoinGuard API",
    description="API for JoinGuard application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc" if DEBUG else None,
    debug=DEBUG
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(list_router)
app.include_router(login_router)
app.include_router(api_router)
app.include_router(report_router)

@app.get("/status")
def read_status():
    return {"Status": "OK"}

@app.get("/form")
def read_form():
    return FileResponse("pages/form.html")

@app.get("/")
def read_index():
    return FileResponse("pages/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv('PORT', 8000)),
        workers=int(os.getenv('WORKERS', 1)),
        log_level="info",
        reload=False
    )