import os
from typing import Any, Dict, Optional, List

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure

MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.api


async def get_nicks() -> Optional[Dict[str, List[str]]]:
    try:
        pipeline = [
            {"$unwind": "$nicknames"},
            {"$group": {"_id": None, "nicknames": {"$addToSet": "$nicknames"}}},
            {"$project": {"_id": 0, "nicknames": 1}}
        ]
        async for document in db.blacklist.aggregate(pipeline):
            return {"data": document["nicknames"]}
        return {"data": []}
    except (ConnectionFailure, OperationFailure):
        return None


async def get_uuids() -> Optional[Dict[str, List[str]]]:
    try:
        pipeline = [
            {"$group": {"_id": None, "uuids": {"$addToSet": "$_id"}}},
            {"$project": {"_id": 0, "uuids": 1}}
        ]
        async for document in db.blacklist.aggregate(pipeline):
            return {"data": document["uuids"]}
        return {"data": []}
    except (ConnectionFailure, OperationFailure):
        return None


async def get_ips() -> Optional[Dict[str, List[str]]]:
    try:
        pipeline = [
            {"$unwind": "$ips"},
            {"$group": {"_id": None, "ips": {"$addToSet": "$ips"}}},
            {"$project": {"_id": 0, "ips": 1}}
        ]
        async for document in db.blacklist.aggregate(pipeline):
            return {"data": document["ips"]}
        return {"data": []}
    except (ConnectionFailure, OperationFailure):
        return None


async def check_api_key(api_key: str) -> Optional[Dict[str, Any]]:
    try:
        query = {"api": api_key, "spam": False}
        document = await db.users.find_one(query)
        if document:
            # Convert the _id from NumberLong to string
            if '_id' in document and isinstance(document['_id'], dict) and '$numberLong' in document['_id']:
                document['_id'] = str(document['_id']['$numberLong'])

            # Add the matched API key to the result
            document['matched_api_key'] = api_key

            return document
        return None
    except (ConnectionFailure, OperationFailure):
        return None

async def mark_api_key_as_spam(api_key: str) -> Optional[Dict[str, str]]:
    try:
        result = await db.users.update_one(
            {"api": api_key},
            {"$set": {"spam": True}}
        )
        if result.modified_count > 0:
            return {"status": "updated", "message": f"Marked API key {api_key} as spam."}
        else:
            return {"status": "no_change", "message": f"API key {api_key} not found or already marked as spam."}
    except (ConnectionFailure, OperationFailure):
        return None


async def upsert_user_data(uuid: str, nickname: Optional[str] = None, ip: Optional[str] = None) -> Optional[
    Dict[str, str]]:
    try:
        update_operations: Dict[str, Any] = {}
        if nickname:
            update_operations["$addToSet"] = {"nicknames": nickname}
        if ip:
            if "$addToSet" in update_operations:
                update_operations["$addToSet"]["ips"] = ip
            else:
                update_operations["$addToSet"] = {"ips": ip}
        if not update_operations:
            return {"status": "no_update", "message": "No data to update"}
        result = await db.blacklist.update_one(
            {"_id": uuid},
            update_operations,
            upsert=True
        )
        if result.matched_count:
            return {"status": "updated", "message": f"Updated user data for UUID: {uuid}"}
        elif result.upserted_id:
            return {"status": "inserted", "message": f"Inserted new user data for UUID: {uuid}"}
        else:
            return {"status": "no_change", "message": f"No update or insert was made for UUID: {uuid}"}
    except (ConnectionFailure, OperationFailure):
        return None


async def is_spam_reporter(discord_id: str) -> Optional[bool]:
    try:
        spam_reporters = await db.config.find_one({"_id": "spam_reporters"})
        if spam_reporters and "reporters" in spam_reporters:
            return discord_id in spam_reporters["reporters"]
        return False
    except (ConnectionFailure, OperationFailure):
        return None


async def add_spam_reporter(discord_id: str) -> Optional[Dict[str, str]]:
    try:
        result = await db.config.update_one(
            {"_id": "spam_reporters"},
            {"$addToSet": {"reporters": discord_id}},
            upsert=True
        )
        if result.modified_count > 0:
            return {"status": "updated", "message": f"Added Discord ID {discord_id} to spam reporters list."}
        elif result.upserted_id:
            return {"status": "inserted", "message": f"Created spam reporters list and added Discord ID {discord_id}."}
        else:
            return {"status": "no_change",
                    "message": f"Discord ID {discord_id} was already in the spam reporters list."}
    except (ConnectionFailure, OperationFailure):
        return None


async def get_all_blacklisted_users() -> Optional[List[Dict[str, Any]]]:
    try:
        cursor = db.blacklist.find({})
        return await cursor.to_list(length=None)
    except (ConnectionFailure, OperationFailure):
        return None
