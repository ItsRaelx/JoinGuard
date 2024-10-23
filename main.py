import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse

# Check if the .env file exists
env_path = '.env'
if os.path.exists(env_path):
    load_dotenv(env_path)

app = FastAPI()

# Import and include router after FastAPI app is created
from routes.list import list_router
from routes.login import login_router
from routes.api import api_router
from routes.report import report_router

app.include_router(list_router)
app.include_router(login_router)
app.include_router(api_router)
app.include_router(report_router)

@app.get("/")
def read_root():
    return {"Status": "OK"}

# Serve the index.html file
@app.get("/main")
def read_index():
    return FileResponse("index.html")


# Run the app
if __name__ == "__main__":
    import uvicorn
    import asyncio


    async def main():
        config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, loop="asyncio")
        server = uvicorn.Server(config)
        await server.serve()


    asyncio.run(main())
