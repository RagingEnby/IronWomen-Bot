from typing import Any
import asyncio
import json

from modules import asyncreqs

import config

SKILL_BRACKETS: dict[str, list[int]] = {
    skill: [level['totalExpRequired']
    for level in data['levels']] for skill, data in config.SKILL_DATA.items()
}
COLLECTION_BRACKETS: dict[str, list[int]] = {
    collection_id: [
        tier['amountRequired']
        for tier in data['tiers']
    ]
    for category in config.COLLECTION_DATA.values()
    for collection_id, data in category['items'].items()
}

async def get(endpoint: str, **kwargs) -> dict[str, Any]:
    params = {"key": config.HYPIXEL_API_KEY}
    params.update(kwargs)
    response = await asyncreqs.get(
        f"https://api.hypixel.net/v2{endpoint}",
        params=params
    )
    if response.status != 200:
        print('GET', response.status, endpoint)
    if response.status == 429:
        await asyncio.sleep(10)
        return await get(endpoint, **kwargs)
    return await response.json()


async def get_profile() -> dict[str, Any]:
    profile = await get("/skyblock/profile", profile=config.PROFILE_ID)
    return profile.get('profile', {})


def calculate_skill(skill: str, exp: int) -> int:
    if skill not in SKILL_BRACKETS:
        raise ValueError(skill)
    brackets = SKILL_BRACKETS[skill]
    lvl = 0
    for bracket in brackets:
        if exp < bracket:
            break
        lvl += 1
    return lvl


def calculate_collection(collection: str, collected: int) -> int:
    if collection not in COLLECTION_BRACKETS:
        raise ValueError(collection)
    brackets = COLLECTION_BRACKETS[collection]
    lvl = 0
    for bracket in brackets:
        if collected < bracket:
            break
        lvl += 1
    return lvl
