import os

import aiohttp

DISCORD_API_ENDPOINT = 'https://discordapp.com/api'
DISCORD_TOKEN_URL = f'{DISCORD_API_ENDPOINT}/oauth2/token'
DISCORD_USER_URL = f'{DISCORD_API_ENDPOINT}/users/@me'

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_oauth_url(state: str, redirect_uri: str = DISCORD_REDIRECT_URI):
    return f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=identify&state={state}"

async def get_code(code: str, redirect_uri: str = DISCORD_REDIRECT_URI):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_TOKEN_URL, data=data, headers=headers) as resp:
            if resp.status != 200:
                return None
            return await resp.json()

async def get_user_data(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}

    async with aiohttp.ClientSession() as session:
        async with session.get(DISCORD_USER_URL, headers=headers) as resp:
            if resp.status != 200:
                return None
            return await resp.json()


async def send_webhook(embed: dict, webhook_url: str = DISCORD_WEBHOOK_URL):
    headers = {'Content-Type': 'application/json'}
    data = {"embeds": [embed]}

    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url, json=data, headers=headers) as resp:
            if resp.status != 204:
                return False
            return True
