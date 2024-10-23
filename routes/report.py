from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

report_router = APIRouter(
    prefix="/report",
    tags=["report"],
)

class ServerData(BaseModel):
    port: str
    ip: str

class ReportedData(BaseModel):
    nick: str
    ip: str
    uuid: str

class ReportingData(BaseModel):
    nick: str

class ReportData(BaseModel):
    server: ServerData
    reported: ReportedData
    reporting: ReportingData
    auth: str
    reason: str

@report_router.post("/")
async def report(report_data: ReportData):
    try:
        print("Received report data:", report_data.dict())
        return JSONResponse(content={"status": "ok", "message": "Report received"})
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error processing request")