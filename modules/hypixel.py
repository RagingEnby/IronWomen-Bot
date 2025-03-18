from typing import Any
import asyncio
from modules import asyncreqs

import config


async def get(endpoint: str, **kwargs) -> dict[str, Any]:
    params = {"key": config.HYPIXEL_API_KEY}
    params.update(kwargs)
    response = await asyncreqs.get(
        f"https://api.hypixel.net/v2{endpoint}",
        params=params
    )
    print('GET', response.status, endpoint)
    if response.status == 429:
        await asyncio.sleep(10)
        return await get(endpoint, **kwargs)
    return await response.json()


async def get_profile() -> dict[str, Any]:
    profile = await get("/skyblock/profile", profile=config.PROFILE_ID)
    return profile.get('profile', {})
    