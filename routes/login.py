import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse

from helpers.discord import get_oauth_url, get_code

login_router = APIRouter(prefix="/login", tags=["login"])

@login_router.get("/oauth2")
async def login(state: str):
    if len(state) > 1024:
        raise HTTPException(status_code=400, detail='State parameter is too long')
    if not re.match(r'^[-A-Za-z0-9+/]*={0,3}$', state):
        raise HTTPException(status_code=400, detail='Invalid state parameter')
    return RedirectResponse(url=get_oauth_url(state))

@login_router.get("/callback")
async def callback(code: str, state: str):
    if not re.match(r'^[-A-Za-z0-9+/]*={0,3}$', state):
        raise HTTPException(status_code=400, detail='Invalid state parameter')
    data = await get_code(code)
    if data is None:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    access_token = data['access_token']
    return RedirectResponse(url=f'/../main?auth={access_token}&state={state}')
