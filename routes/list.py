from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from helpers.database import get_uuids, get_nicks, get_ips

list_router = APIRouter(prefix="/list", tags=["list"])

class ListModel(BaseModel):
    names: list[str]

class UUIDModel(BaseModel):
    uuids: list[str]

class IPModel(BaseModel):
    ips: list[str]

@list_router.get("/name", response_model=ListModel)
async def read_nicks():
    result = await get_nicks()
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return result

@list_router.get("/uuid", response_model=UUIDModel)
async def read_uuids():
    result = await get_uuids()
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return result

@list_router.get("/ip", response_model=IPModel)
async def read_ips():
    result = await get_ips()
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return result
