from fastapi import APIRouter
from fastapi import Request
import re
from fastapi.responses import RedirectResponse

from helpers.discord import get_oauth_url, get_code, get_user_data

login_router = APIRouter(
    prefix="/login",
    tags=["login"],
)


@login_router.get("/oauth2")
async def login(state: str):
    # Make sure it isn't longer than 1024 characters
    if len(state) > 1024:
        raise ValueError('State parameter is too long')

    # Make sure it is a base64 like string
    if not re.match(r'^[-A-Za-z0-9+/]*={0,3}$', state):
        raise ValueError('Invalid state parameter')
    return RedirectResponse(url=get_oauth_url(state))


@login_router.get("/callback")
async def callback(code: str, state: str):
    if not re.match(r'^[-A-Za-z0-9+/]*={0,3}$', state):
        raise ValueError('Invalid state parameter')

    data = await get_code(code)
    access_token = data['access_token']
    return RedirectResponse(url='/../main?auth=' + access_token + '&state=' + state)
