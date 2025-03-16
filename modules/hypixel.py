from typing import Any
import asyncio
from modules import asyncreqs

import config


async def get(endpoint: str, **kwargs) -> dict[str, Any]:
    response = await asyncreqs.get(
        f"https://api.hypixel.net/v2{endpoint}",
        params=kwargs
    )
    if response.status == 429:
        await asyncio.sleep(10)
        return await get(endpoint, **kwargs)
    return await response.json()


async def get_profile() -> dict[str, Any]:
    profile = await get("/skyblock/profile", profile=config.PROFILE_ID)
    return profile.get('profile', {})
    