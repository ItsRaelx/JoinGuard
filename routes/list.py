from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from helpers.database import get_uuids, get_nicks, get_ips
from helpers.hashing import hash_data_with_salt

list_router = APIRouter(prefix="/list", tags=["list"])


class DataModel(BaseModel):
    data: list[str]


@list_router.get("/name", response_model=DataModel)
async def read_nicks():
    result = await get_nicks()
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return result


@list_router.get("/uuid", response_model=DataModel)
async def read_uuids():
    result = await get_uuids()
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return result


@list_router.get("/ip", response_model=DataModel)
async def read_ips():
    result = await get_ips()
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    hashed_result = await hash_data_with_salt(result['data'] if isinstance(result, dict) and 'data' in result else result)
    return {"data": hashed_result}