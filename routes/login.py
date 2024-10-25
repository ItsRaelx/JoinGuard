from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from helpers.discord import get_oauth_url, get_code
from helpers.models import StateModel, CallbackModel

login_router = APIRouter(prefix="/login", tags=["login"])


@login_router.get("/oauth2")
async def login(state_data: StateModel = Depends()):
    return RedirectResponse(url=get_oauth_url(state_data.state))


@login_router.get("/callback")
async def callback(callback_data: CallbackModel = Depends()):
    data = await get_code(callback_data.code)
    if data is None:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    access_token = data['access_token']
    return RedirectResponse(url=f'/../form?auth={access_token}&state={callback_data.state}')
