import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes.api import api_router
from routes.list import list_router
from routes.login import login_router
from routes.report import report_router

# Load environment variables
env_path = '.env'
if os.path.exists(env_path):
    load_dotenv(env_path)

app = FastAPI()

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


@app.get("/report")
def read_index():
    return FileResponse("pages/report.html")


@app.get("/")
def read_index():
    return FileResponse("pages/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
