from fastapi import APIRouter
from pydantic import BaseModel
from helpers.database import get_uuids, get_nicks, get_ips

list_router = APIRouter(
    prefix="/list",
    tags=["list"],
)

class ListModel(BaseModel):
    names: list[str]

class UUIDModel(BaseModel):
    uuids: list[str]

class IPModel(BaseModel):
    ips: list[str]

@list_router.get("/name", response_model=ListModel)
async def read_nicks():
    return await get_nicks()

@list_router.get("/uuid", response_model=UUIDModel)
async def read_uuids():
    return await get_uuids()

@list_router.get("/ip", response_model=IPModel)
async def read_ips():
    return await get_ips()