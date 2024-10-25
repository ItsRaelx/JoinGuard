from datetime import datetime
from os import getenv

from fastapi import APIRouter, HTTPException, Depends
from starlette.responses import HTMLResponse, RedirectResponse

from helpers.database import check_api_key, add_api_key, get_api_key_count, is_spam_reporter
from helpers.discord import send_webhook, get_code, get_user_data, get_oauth_url
from helpers.models import LoginAttemptModel, ApiResponse, AltsReportModel, APICallbackModel, StateModel
from helpers.signing import generate_signed_url

DISCORD_WEBHOOK_ATTEMPT_URL = getenv("DISCORD_WEBHOOK_ATTEMPT_URL")
DISCORD_WEBHOOK_ALTS_URL = getenv("DISCORD_WEBHOOK_ALTS_URL")
DISCORD_REDIRECT_URI_API = getenv("DISCORD_REDIRECT_URI_API")

api_router = APIRouter(prefix="/api", tags=["api"])


@api_router.get("/register", response_class=HTMLResponse)
async def login(state_data: StateModel = Depends()):
    return RedirectResponse(url=get_oauth_url(state_data.state, redirect_uri=DISCORD_REDIRECT_URI_API))


@api_router.get("/callback")
async def callback(callback_data: APICallbackModel = Depends()):
    data = await get_code(callback_data.code, redirect_uri=DISCORD_REDIRECT_URI_API)
    if data is None:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    access_token = data['access_token']

    # get user id
    user_data = await get_user_data(access_token)
    if user_data is None:
        raise HTTPException(status_code=400, detail="Failed to get user data")
    user_id = user_data.get('id')

    # check if user is in spam reporters list
    is_spammer = await is_spam_reporter(user_id)
    if is_spammer is None:
        raise HTTPException(status_code=500, detail="Database error")
    if is_spammer:
        raise HTTPException(status_code=403, detail="User is marked as a spammer")

    # get how many api keys the user has
    api_count = await get_api_key_count(user_id)
    if api_count is None:
        raise HTTPException(status_code=500, detail="Database error")

    # if user has less 10 api keys, add one
    if api_count <= 10:
        result = await add_api_key(user_id, callback_data.state)
        if result is None:
            raise HTTPException(status_code=500, detail="Database error")
    else:
        raise HTTPException(status_code=403, detail="User has reached the maximum number of API keys")

    # add api key to user
    result = await add_api_key(user_id, callback_data.state)
    if result is None:
        raise HTTPException(status_code=500, detail="Database error")
    return ApiResponse(status="ok", message="API key added")



@api_router.get("/check", response_model=ApiResponse)
async def check_api_route(api: str):
    result = await check_api_key(api)
    if not result:
        return ApiResponse(status="Invalid API key", message="You have provided an invalid API key")
    return ApiResponse(status="ok", message="Valid API key")

@api_router.post("/attempt", response_model=ApiResponse)
async def login_attempt(attempt: LoginAttemptModel):
    result = await check_api_key(attempt.api)
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
    result = await check_api_key(report.api)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if not DISCORD_WEBHOOK_ALTS_URL:
        raise HTTPException(status_code=500, detail="Webhook URL is not configured")

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
        "color": 15105570,
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
