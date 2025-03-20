import requests
from typing import Any

# Hypixel
PROFILE_ID: str = "9c2dfcc9-5745-41d3-8932-998813bedbca"
## Secrets
HYPIXEL_API_KEY: str = "15ce4c9a-a68e-4387-a818-92facb410378"
## API Data
SKILL_DATA: dict[str, dict[str, Any]] = requests.get('https://api.hypixel.net/v2/resources/skyblock/skills').json()['skills']
COLLECTION_DATA: dict[str, dict[str, Any]] = requests.get('https://api.hypixel.net/v2/resources/skyblock/collections').json()['collections']

# Discord
## Discord ID's
RAGINGENBY_USER_ID: int = 447861538095759365
SB_LEVEL_CHANNEL_ID: int = 1350921735561805935
BANK_CHANNEL_ID: int = 1351233946020610179
COLLECTION_CHANNEL_ID: int = 1352331906301034509
SKILL_CHANNEL_ID: int = 1352336154753503375
## Secrets
BOT_TOKEN: str = "MTM1MDkxOTM2MTI3NTM2NzU3NQ.GhFHaQ.0tYqcL3f6tu0hOH0YJEkd68iMu6LzaZyXvNcDE"


STEVE_AVATAR: str = "https://mc-heads.net/avatar/c06f89064c8a49119c29ea1dbd1aab82"
