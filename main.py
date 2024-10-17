import os

from dotenv import load_dotenv
from fastapi import FastAPI

# Check if the .env file exists
env_path = '.env'
if os.path.exists(env_path):
    load_dotenv(env_path)

app = FastAPI()

# Import and include router after FastAPI app is created
from routes.list import list_router

app.include_router(list_router)


@app.get("/")
def read_root():
    return {"Status": "OK"}


# Run the app
if __name__ == "__main__":
    import uvicorn
    import asyncio


    async def main():
        config = uvicorn.Config("main:app", host="0.0.0.0", port=8000, loop="asyncio")
        server = uvicorn.Server(config)
        await server.serve()


    asyncio.run(main())
