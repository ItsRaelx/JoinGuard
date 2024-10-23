import os

import aiohttp
from fastapi import HTTPException

DISCORD_API_ENDPOINT = 'https://discordapp.com/api'
DISCORD_TOKEN_URL = f'{DISCORD_API_ENDPOINT}/oauth2/token'
DISCORD_USER_URL = f'{DISCORD_API_ENDPOINT}/users/@me'

# Get DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET and DISCORD_REDIRECT_URI from environment variables
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")


def get_oauth_url(state: str):
    return f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20email&state={state}"

# Exchange the code for an access token
async def get_code(code: str):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_TOKEN_URL, data=data, headers=headers) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=400, detail="Failed to get access token")
            return await resp.json()

async def get_user_data(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(DISCORD_USER_URL, headers=headers) as resp:
            if resp.status != 200:
                return None
            return await resp.json()