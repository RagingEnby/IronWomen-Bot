import aiohttp
from typing import Optional

SESSSION: Optional[aiohttp.ClientSession] = None


async def get(*args, **kwargs) -> aiohttp.ClientResponse:
    global SESSSION
    if not SESSION or SESSION.closed:
        SESSION = aiohttp.ClientSession()
    return await SESSION.get(*args, **kwargs)
    