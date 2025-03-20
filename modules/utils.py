import disnake
import json
from typing import Optional
import aiofiles
import re

import constants as g


async def send_to_channel(channel_id: int, *args, **kwargs) -> Optional[disnake.Message]:
    channel = g.BOT.get_channel(channel_id)
    if not channel:
        print('unable to find channel', channel_id)
        return None
    return await channel.send(*args, **kwargs)  # type: ignore


async def write_json(file_path: str, data, indent: int | None = 2):
    async with aiofiles.open(file_path, 'w') as file:
        await file.write(json.dumps(data, indent=indent))


def remove_color_codes(string: str) -> str:
    return re.sub(r'§[0-9a-fA-F]', '', string)


def dict_diff(d1: dict, d2: dict) -> dict:
    diff = {}
    for key in d2:
        if key not in d1:
            diff[key] = d2[key]
        else:
            if isinstance(d2[key], dict) and isinstance(d1[key], dict):
                nested_diff = dict_diff(d1[key], d2[key])
                if nested_diff:
                    diff[key] = nested_diff
            elif d2[key] != d1[key]:
                diff[key] = d2[key]
    return diff


def commaize(number: int | float) -> str:
    return '{:,}'.format(round(number, 2))
    