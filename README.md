# JoinGuard

JoinGuard is a robust solution designed to safeguard your Minecraft server against disruptive players. It combines a
Minecraft plugin with a web service to provide a seamless reporting and blacklisting system.

## Features

- Player reporting system
- Integration with Discord for report management
- Automatic blacklisting of reported players
- Spam reporter detection
- Secure API with OAuth2 authentication

## Components

1. Minecraft Plugin: Generates initial report data and URL (plugin will be linked here in the future)
2. Web Service: Handles report submission, verification, and blacklist management
3. Discord Integration: Displays reports and allows moderator actions

## Setup

### Prerequisites

- Python 3.7+
- MongoDB
- Discord Developer Account

### Web Service Setup

1. Clone the repository: `git clone https://github.com/ItsRaelx/JoinGuard.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Create a .env file in the project root and add the following variables:

```
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=
DISCORD_WEBHOOK_URL=
MONGO_URI=
SIGN_SECRET=
```

4. Run the web service: `python main.py`

## API Usage

### Endpoints

- /api/check: Check if the API key is valid and not marked as spam
- /api/login: OAuth2 authentication endpoint
- /api/report: Report player data
- /api/list/name: Get all unique nicknames
- /api/list/uuid: Get all unique UUIDs
- /api/list/ip: Get all unique IPs

## Security

The web service uses a secret key to sign URLs and verify them. This key should be kept secret and not shared with
anyone. It is recommended to use a long, random string as the secret key.

Discord webhooks are used to send notifications to Discord channels. The webhook URL should be kept secret and not
shared with anyone. It is recommended to use a long, random string as the webhook URL.

The web service uses OAuth2 authentication to authenticate users. The client ID and client secret should be kept secret
and not shared with anyone. It is recommended to use a long, random string as the client ID and client secret.

## Hosting and Development

Please note that only RAIDVM is authorized to host and further develop this software. Unauthorized hosting or
modification of this software is not permitted.

## Contributing

If you find any issues or have suggestions for improvement, please open an issue or submit a pull request.

## License

You are not permitted to host or distribute this software without the express written consent of the author. (Except for
sharing the link to this repository)