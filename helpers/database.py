import os
from typing import Any
from typing import Dict, Optional
from typing import List

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Get MONGO_URI from environment variable directly
MONGO_URI = os.getenv("MONGO_URI")

# Asynchronous MongoDB connection
client = AsyncIOMotorClient(MONGO_URI)
db = client.api


async def get_nicks() -> Dict[str, List[str]]:
    """
    Retrieve all unique nicknames from the blacklist.
    """
    try:
        pipeline = [
            {"$unwind": "$nicknames"},
            {"$group": {"_id": None, "nicknames": {"$addToSet": "$nicknames"}}},
            {"$project": {"_id": 0, "nicknames": 1}}
        ]
        async for document in db.blacklist.aggregate(pipeline):
            return {"names": document["nicknames"]}
        return {"names": []}
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail="Database connection error")
    except OperationFailure:
        raise HTTPException(status_code=500, detail="Database operation error")


async def get_uuids() -> Dict[str, List[str]]:
    """
    Retrieve all unique UUIDs from the blacklist.
    """
    try:
        pipeline = [
            {"$group": {"_id": None, "uuids": {"$addToSet": "$_id"}}},
            {"$project": {"_id": 0, "uuids": 1}}
        ]
        async for document in db.blacklist.aggregate(pipeline):
            return {"uuids": document["uuids"]}
        return {"uuids": []}
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail="Database connection error")
    except OperationFailure:
        raise HTTPException(status_code=500, detail="Database operation error")


async def get_ips() -> Dict[str, List[str]]:
    """
    Retrieve all unique IPs from the blacklist.
    """
    try:
        pipeline = [
            {"$unwind": "$ips"},
            {"$group": {"_id": None, "ips": {"$addToSet": "$ips"}}},
            {"$project": {"_id": 0, "ips": 1}}
        ]
        async for document in db.blacklist.aggregate(pipeline):
            return {"ips": document["ips"]}
        return {"ips": []}
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail="Database connection error")
    except OperationFailure:
        raise HTTPException(status_code=500, detail="Database operation error")


async def check_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Check if the given API key is valid and not marked as spam.
    """
    try:
        query = {
            "_id": api_key,
            "spam": False
        }
        document = await db.users.find_one(query)

        if document:
            # Convert discord NumberLong to string
            if 'discord' in document and isinstance(document['discord'], int):
                document['discord'] = str(document['discord'])
            return document

        return None
    except ConnectionFailure:
        raise HTTPException(status_code=503, detail="Database connection error")
    except OperationFailure:
        raise HTTPException(status_code=500, detail="Database operation error")