import re
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from helpers.database import check_api_key, upsert_user_data, add_spam_reporter, mark_api_key_as_spam
from helpers.discord import send_webhook
from helpers.models import LoginResponse, LoginAttemptModel, LoginModel, ApiKeySpamModel, BlacklistAddModel, ApiResponse
from helpers.signing import generate_signed_url, verify_signed_url
from os import getenv

DISCORD_WEBHOOK_ATTEMPT_URL = getenv("DISCORD_WEBHOOK_ATTEMPT_URL")

api_router = APIRouter(prefix="/api", tags=["api"])

@api_router.get("/check", response_model=LoginResponse)
async def check_api_key_route(api_key: str):
    result = await check_api_key(api_key)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return LoginResponse(data=LoginModel(**result))

@api_router.post("/attempt", response_model=ApiResponse)
async def login_attempt(attempt: LoginAttemptModel):
    result = await check_api_key(attempt.api_key)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")

    blacklist_data = BlacklistAddModel(
        nick=attempt.player.nick,
        ip=attempt.player.ip,
        uuid=attempt.player.uuid
    )
    spam_data = ApiKeySpamModel(api_key=attempt.api_key)

    blacklist_url = generate_signed_url("https://joinguard.raidvm.com/api/add", blacklist_data.dict())
    spam_url = generate_signed_url("https://joinguard.raidvm.com/api/spam", spam_data.dict())

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

@api_router.get("/add", response_model=ApiResponse)
async def add_to_blacklist(blacklist_data: BlacklistAddModel = Depends()):
    if not verify_signed_url(blacklist_data.dict()):
        raise HTTPException(status_code=400, detail="Invalid or expired URL")

    result = await upsert_user_data(blacklist_data.uuid, blacklist_data.nick, blacklist_data.ip)
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return ApiResponse(**result)

@api_router.get("/spam", response_model=ApiResponse)
async def mark_as_spam(spam_data: ApiKeySpamModel = Depends()):
    if not verify_signed_url(spam_data.dict()):
        raise HTTPException(status_code=400, detail="Invalid or expired URL")

    result = await mark_api_key_as_spam(spam_data.api_key)
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return ApiResponse(**result)