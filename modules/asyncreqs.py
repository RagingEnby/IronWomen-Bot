import aiohttp
from typing import Optional

SESSION: Optional[aiohttp.ClientSession] = None


async def get(*args, **kwargs) -> aiohttp.ClientResponse:
    global SESSION
    if not SESSION or SESSION.closed:
        SESSION = aiohttp.ClientSession()
    response = await SESSION.get(*args, **kwargs)
    print(response.status, response.url)
    return response
    