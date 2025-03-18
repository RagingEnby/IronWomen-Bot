import aiohttp
from typing import Optional

SESSION: Optional[aiohttp.ClientSession] = None


async def get(*args, **kwargs) -> aiohttp.ClientResponse:
    global SESSION
    if not SESSION or SESSION.closed:
        SESSION = aiohttp.ClientSession()
        return await get(*args, **kwargs)
    return await SESSION.get(*args, **kwargs)
    