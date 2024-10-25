from datetime import datetime
from os import getenv

from fastapi import APIRouter, HTTPException

from helpers.database import check_api_key
from helpers.discord import send_webhook
from helpers.models import LoginAttemptModel, ApiResponse, AltsReportModel
from helpers.signing import generate_signed_url

DISCORD_WEBHOOK_ATTEMPT_URL = getenv("DISCORD_WEBHOOK_ATTEMPT_URL")
DISCORD_WEBHOOK_ALTS_URL = getenv("DISCORD_WEBHOOK_ALTS_URL")

api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.get("/check", response_model=ApiResponse)
async def check_api_key_route(api_key: str):
    result = await check_api_key(api_key)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return ApiResponse(status="ok", message="Valid API key")

@api_router.post("/attempt", response_model=ApiResponse)
async def login_attempt(attempt: LoginAttemptModel):
    result = await check_api_key(attempt.api_key)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")

    blacklist_data = {
        "nick": attempt.player.nick,
        "ip": attempt.player.ip,
        "uuid": attempt.player.uuid
    }
    blacklist_url = generate_signed_url("https://joinguard.raidvm.com/report/add", blacklist_data)

    spam_data = {"user_id": result.get('id')}
    spam_url = generate_signed_url("https://joinguard.raidvm.com/report/spam", spam_data)

    embed = {
        "title": "Szczegóły \"Attempt\"",
        "color": 5814783,
        "footer": {"text": "JoinGuard"},
        "timestamp": datetime.now().isoformat(),
        "thumbnail": {"url": f"https://mc-heads.net/avatar/{attempt.player.uuid}"},
        "fields": [
            {"name": "Nickname", "value": attempt.player.nick, "inline": True},
            {"name": "IP", "value": attempt.player.ip, "inline": True},
            {"name": "Server", "value": f"{attempt.server.ip}:{attempt.server.port}", "inline": True},
            {"name": "UUID", "value": attempt.player.uuid, "inline": True},
            {"name": "Blacklista", "value": f"[Dodaj]({blacklist_url}) | [Spam]({spam_url})", "inline": False},
        ]
    }

    await send_webhook(embed, webhook_url=DISCORD_WEBHOOK_ATTEMPT_URL)
    return ApiResponse(status="ok", message="Attempt logged")


@api_router.post("/alts", response_model=ApiResponse)
async def report_alts(report: AltsReportModel):
    result = await check_api_key(report.api_key)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")

    blacklist_data = {
        "nick": report.player.nick,
        "ip": report.player.ip,
        "uuid": report.player.uuid
    }
    blacklist_url = generate_signed_url("https://joinguard.raidvm.com/report/add", blacklist_data)

    spam_data = {"user_id": result.get('id')}
    spam_url = generate_signed_url("https://joinguard.raidvm.com/report/spam", spam_data)

    alts_list = ", ".join(report.alts) if report.alts else "None reported"

    embed = {
        "title": "Alts Report",
        "color": 15105570,  # A different color to distinguish from login attempts
        "footer": {"text": "JoinGuard"},
        "timestamp": datetime.now().isoformat(),
        "thumbnail": {"url": f"https://mc-heads.net/avatar/{report.player.uuid}"},
        "fields": [
            {"name": "Nickname", "value": report.player.nick, "inline": True},
            {"name": "IP", "value": report.player.ip, "inline": True},
            {"name": "Server", "value": f"{report.server.ip}:{report.server.port}", "inline": True},
            {"name": "UUID", "value": report.player.uuid, "inline": True},
            {"name": "Alts", "value": alts_list, "inline": False},
            {"name": "Actions", "value": f"[Add to Blacklist]({blacklist_url}) | [Mark as Spam]({spam_url})",
             "inline": False},
        ]
    }

    await send_webhook(embed, webhook_url=DISCORD_WEBHOOK_ALTS_URL)
    return ApiResponse(status="ok", message="Alts report received")
