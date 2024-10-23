from datetime import datetime

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from helpers.database import upsert_user_data, is_spam_reporter, add_spam_reporter
from helpers.discord import send_webhook, get_user_data
from helpers.signing import generate_signed_url, verify_signed_url

report_router = APIRouter(prefix="/report", tags=["report"])

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
    user_data = await get_user_data(report_data.auth)
    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid API key")

    is_spammer = await is_spam_reporter(user_data.get('id'))
    if is_spammer is None:
        raise HTTPException(status_code=500, detail="Database error")
    if is_spammer:
        raise HTTPException(status_code=403, detail="User is marked as a spammer")

    try:
        blacklist_data = {
            "nick": report_data.reported.nick,
            "ip": report_data.reported.ip,
            "uuid": report_data.reported.uuid,
        }
        spam_data = {"user_id": user_data.get('id')}

        blacklist_url = generate_signed_url("https://joinguard.raidvm.com/report/add", blacklist_data)
        spam_url = generate_signed_url("https://joinguard.raidvm.com/report/spam", spam_data)

        embed = {
            "title": "Szczegóły zgłoszenia",
            "color": 5814783,
            "footer": {"text": "JoinGuard"},
            "author": {
                "name": f"Zgłosił: DC - {user_data.get('username', 'Unknown')}, MC - {report_data.reporting.nick}",
                "url": f"https://discordapp.com/users/{user_data.get('id', 'Unknown')}",
                "icon_url": f"https://cdn.discordapp.com/avatars/{user_data.get('id', 'Unknown')}/{user_data['avatar']}.png",
            },
            "timestamp": datetime.now().isoformat(),
            "thumbnail": {"url": f"https://mc-heads.net/avatar/{report_data.reported.uuid}"},
            "fields": [
                {"name": "Nickname", "value": report_data.reported.nick, "inline": True},
                {"name": "IP", "value": report_data.reported.ip, "inline": True},
                {"name": "Server", "value": f"{report_data.server.ip}:{report_data.server.port}", "inline": True},
                {"name": "UUID", "value": report_data.reported.uuid, "inline": True},
                {"name": "Powód", "value": report_data.reason, "inline": False},
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

    result = await upsert_user_data(params['uuid'], params['nick'], params['ip'])
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return JSONResponse(content=result)


@report_router.get("/spam")
async def mark_as_spam(request: Request):
    params = dict(request.query_params)
    if not verify_signed_url(params):
        raise HTTPException(status_code=400, detail="Invalid or expired URL")

    result = await add_spam_reporter(params['user_id'])
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return JSONResponse(content=result)
