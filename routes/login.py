from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from helpers.discord import get_oauth_url, get_code

login_router = APIRouter(prefix="/login", tags=["login"])


class StateModel(BaseModel):
    state: str = Field(..., max_length=1024, pattern=r'^[-A-Za-z0-9+/]*={0,3}$')


class CallbackModel(BaseModel):
    code: str = Field(..., pattern=r'^[A-Za-z0-9]{30}$')
    state: str = Field(..., max_length=1024, pattern=r'^[-A-Za-z0-9+/]*={0,3}$')


@login_router.get("/oauth2")
async def login(state_data: StateModel = Depends()):
    return RedirectResponse(url=get_oauth_url(state_data.state))


@login_router.get("/callback")
async def callback(callback_data: CallbackModel = Depends()):
    data = await get_code(callback_data.code)
    if data is None:
        raise HTTPException(status_code=400, detail="Failed to get access token")
    access_token = data['access_token']
    return RedirectResponse(url=f'/../report?auth={access_token}&state={callback_data.state}')
