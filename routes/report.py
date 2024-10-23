import re
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from helpers.database import upsert_user_data, is_spam_reporter, add_spam_reporter
from helpers.discord import send_webhook, get_user_data
from helpers.signing import generate_signed_url, verify_signed_url

report_router = APIRouter(prefix="/report", tags=["report"])

class ServerData(BaseModel):
    port: str = Field(..., pattern=r'^\d{1,5}$')
    ip: str = Field(..., pattern=r'^(\d{1,3}\.){3}\d{1,3}$')

class ReportedData(BaseModel):
    nick: str = Field(..., pattern=r'^[a-zA-Z0-9_]{3,16}$')
    ip: str = Field(..., pattern=r'^(\d{1,3}\.){3}\d{1,3}$')
    uuid: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

class ReportingData(BaseModel):
    nick: str = Field(..., pattern=r'^[a-zA-Z0-9_]{3,16}$')

class ReportData(BaseModel):
    server: ServerData
    reported: ReportedData
    reporting: ReportingData
    auth: str = Field(..., pattern=r'^[A-Za-z0-9-_]{30,}$')
    reason: str = Field(..., max_length=1000)

    @validator('reason')
    def reason_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Reason cannot be empty')
        return v

    def serialize(self) -> Dict[str, Any]:
        return {
            "server": {
                "port": str(self.server.port),
                "ip": str(self.server.ip)
            },
            "reported": {
                "nick": str(self.reported.nick),
                "ip": str(self.reported.ip),
                "uuid": str(self.reported.uuid)
            },
            "reporting": {
                "nick": str(self.reporting.nick)
            },
            "auth": str(self.auth),
            "reason": str(self.reason)
        }

@report_router.post("/")
async def report(report_data: ReportData):
    serialized_data = report_data.serialize()
    user_data = await get_user_data(serialized_data["auth"])
    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    is_spammer = await is_spam_reporter(str(user_data.get('id')))
    if is_spammer is None:
        raise HTTPException(status_code=500, detail="Database error")
    if is_spammer:
        raise HTTPException(status_code=403, detail="User is marked as a spammer")

    try:
        blacklist_data = {
            "nick": serialized_data["reported"]["nick"],
            "ip": serialized_data["reported"]["ip"],
            "uuid": serialized_data["reported"]["uuid"],
        }
        spam_data = {"user_id": str(user_data.get('id'))}

        blacklist_url = generate_signed_url("https://joinguard.raidvm.com/report/add", blacklist_data)
        spam_url = generate_signed_url("https://joinguard.raidvm.com/report/spam", spam_data)

        embed = {
            "title": "Szczegóły zgłoszenia",
            "color": 5814783,
            "footer": {"text": "JoinGuard"},
            "author": {
                "name": f"Zgłosił: DC - {str(user_data.get('username', 'Unknown'))}, MC - {serialized_data['reporting']['nick']}",
                "url": f"https://discordapp.com/users/{str(user_data.get('id', 'Unknown'))}",
                "icon_url": f"https://cdn.discordapp.com/avatars/{str(user_data.get('id', 'Unknown'))}/{str(user_data.get('avatar', ''))}",
            },
            "timestamp": datetime.now().isoformat(),
            "thumbnail": {"url": f"https://mc-heads.net/avatar/{serialized_data['reported']['uuid']}"},
            "fields": [
                {"name": "Nickname", "value": serialized_data["reported"]["nick"], "inline": True},
                {"name": "IP", "value": serialized_data["reported"]["ip"], "inline": True},
                {"name": "Server", "value": f"{serialized_data['server']['ip']}:{serialized_data['server']['port']}",
                 "inline": True},
                {"name": "UUID", "value": serialized_data["reported"]["uuid"], "inline": True},
                {"name": "Powód", "value": serialized_data["reason"], "inline": False},
                {"name": "Blacklista", "value": f"[Dodaj]({blacklist_url}) | [Spam]({spam_url})", "inline": False},
            ]
        }

        if not await send_webhook(embed):
            raise HTTPException(status_code=500, detail="Failed to send webhook")
        return JSONResponse(content={"status": "ok", "message": "Report received"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing request: {str(e)}")

@report_router.get("/add")
async def add_to_blacklist(request: Request):
    params = dict(request.query_params)
    if not verify_signed_url(params):
        raise HTTPException(status_code=400, detail="Invalid or expired URL")

    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    nick_pattern = r'^[a-zA-Z0-9_]{3,16}$'
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'

    if not re.match(uuid_pattern, params.get('uuid', '')):
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    if not re.match(nick_pattern, params.get('nick', '')):
        raise HTTPException(status_code=400, detail="Invalid nickname format")
    if not re.match(ip_pattern, params.get('ip', '')):
        raise HTTPException(status_code=400, detail="Invalid IP format")

    result = await upsert_user_data(params['uuid'], params['nick'], params['ip'])
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return JSONResponse(content=result)

@report_router.get("/spam")
async def mark_as_spam(request: Request):
    params = dict(request.query_params)
    if not verify_signed_url(params):
        raise HTTPException(status_code=400, detail="Invalid or expired URL")

    user_id_pattern = r'^\d{17,19}$'
    if not re.match(user_id_pattern, params.get('user_id', '')):
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    result = await add_spam_reporter(params['user_id'])
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return JSONResponse(content=result)